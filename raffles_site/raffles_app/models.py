from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets, hashlib, random, uuid

class Profile(models.Model):
    """
    Perfil extendido para cada usuario.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    document_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def raffles_participated(self):
        return Raffle.objects.filter(tickets__user=self.user).distinct()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)



class Motorcycle(models.Model):
    """
    Representa la moto que será rifada.
    Puede ser nueva o usada.
    """
    brand = models.CharField(max_length=100, db_index=True)   # Ej: Yamaha
    model = models.CharField(max_length=100, db_index=True)   # Ej: MT-09
    year = models.PositiveIntegerField(db_index=True)         # Ej: 2024
    description = models.TextField(blank=True)

    # Estado de la moto
    is_new = models.BooleanField(default=True)     # True = nueva, False = usada
    mileage = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Kilometraje en kilómetros (solo si es usada)."
    )
    condition = models.CharField(
        max_length=50,
        choices=[
            ("excelente", "Excelente"),
            ("bueno", "Bueno"),
            ("regular", "Regular"),
        ],
        blank=True,
        null=True,
        help_text="Condición general de la moto si es usada."
    )

    def __str__(self):
        estado = "Nueva" if self.is_new else f"Usada - {self.mileage or 0} km"
        return f"{self.brand} {self.model} ({self.year}) - {estado}"


class MotorcycleImage(models.Model):
    """
    Permite asociar múltiples imágenes a una misma moto.
    """
    motorcycle = models.ForeignKey(
        Motorcycle,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="motos/")

    def __str__(self):
        return f"Imagen de {self.motorcycle.brand} {self.motorcycle.model}"


class Raffle(models.Model):
    """
    Representa una rifa de una moto específica.
    Maneja la lógica de transparencia con commit-reveal.
    """
    STATUS_CHOICES = [
        ("open", "Abierta"),
        ("closed", "Cerrada"),
        ("finished", "Finalizada con ganador"),
    ]

    motorcycle = models.ForeignKey(
        Motorcycle,
        on_delete=models.CASCADE,
        related_name="raffles"
    )
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_tickets = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ends_at = models.DateTimeField()

    # Transparencia del sorteo
    seed_commitment = models.CharField(max_length=128, blank=True, null=True)
    seed_reveal = models.CharField(max_length=256, blank=True, null=True)
    winner_ticket = models.ForeignKey(
        'Ticket',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_raffles"
    )

    def __str__(self):
        return f"Rifa: {self.motorcycle}"

    # -------- Métodos de negocio -------- #
    def create_commit(self):
        """Genera el compromiso inicial (commit) con un seed seguro."""
        seed = secrets.token_hex(32)
        h = hashlib.sha256(seed.encode()).hexdigest()
        self.seed_reveal = seed
        self.seed_commitment = h
        self.save()
        return h

    def verify_commit(self):
        """Verifica que el seed_reveal coincide con el seed_commitment."""
        if not self.seed_reveal or not self.seed_commitment:
            return False
        return hashlib.sha256(self.seed_reveal.encode()).hexdigest() == self.seed_commitment

    def pick_winner_commit_reveal(self):
        """Selecciona un ganador de manera transparente."""
        tickets = list(self.tickets.all())
        if not tickets:
            return None

        if not self.verify_commit():
            raise ValueError("Seed reveal no coincide con el commitment.")

        digest = hashlib.sha256((self.seed_reveal + str(len(tickets))).encode()).hexdigest()
        idx = int(digest, 16) % len(tickets)
        winner = tickets[idx]
        self.winner_ticket = winner
        self.status = "finished"
        self.save()
        return winner

    def available_tickets(self):
        """Cuántos tickets quedan disponibles."""
        ocupados = self.tickets.count()
        return self.max_tickets - ocupados

    def is_active(self):
        """Devuelve True si la rifa está abierta y con tickets disponibles."""
        return self.status == "open" and self.available_tickets() > 0

    @property
    def winner_user(self):
        """Devuelve el usuario ganador si ya existe uno."""
        return self.winner_ticket.user if self.winner_ticket else None

    def user_has_ticket(self, user):
        """Retorna True si un usuario ya tiene un ticket en esta rifa."""
        return self.tickets.filter(user=user).exists()


class Ticket(models.Model):
    """
    Representa la boleta comprada por un usuario en una rifa de motos.
    Puede elegirse manualmente o asignarse de forma aleatoria.
    """
    PAYMENT_STATUS = [
        ("pending", "Pendiente"),
        ("paid", "Pagado"),
        ("failed", "Fallido"),
    ]

    raffle = models.ForeignKey(
        Raffle,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    number = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Código único
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="pending",
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('raffle', 'number')
        ordering = ['number']

    def save(self, *args, **kwargs):
        """Asignar número aleatorio si no se pasa, validar rango y duplicados."""
        if self.number is None:
            posibles = set(range(1, self.raffle.max_tickets + 1))
            ocupados = set(
                Ticket.objects.filter(raffle=self.raffle).values_list("number", flat=True)
            )
            libres = list(posibles - ocupados)
            if not libres:
                raise ValueError("No quedan boletas disponibles en esta rifa.")
            self.number = random.choice(libres)
        else:
            if self.number < 1 or self.number > self.raffle.max_tickets:
                raise ValueError("El número elegido está fuera del rango permitido.")
            if Ticket.objects.filter(raffle=self.raffle, number=self.number).exists():
                raise ValueError(f"La boleta {self.number} ya está ocupada en esta rifa.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Boleta {self.number} - {self.user.username} en {self.raffle}"


class CarouselSlide(models.Model):
    """Slide para el carrusel del home."""
    title = models.CharField(max_length=100, blank=True, help_text="Título opcional del slide")
    subtitle = models.CharField(max_length=200, blank=True, help_text="Subtítulo o descripción")
    image = models.ImageField(upload_to="carousel/", help_text="Imagen principal del slide")
    link = models.URLField(blank=True, help_text="Link opcional al que redirige el slide")
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición en el carrusel")
    is_active = models.BooleanField(default=True, help_text="Mostrar este slide en el carrusel")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or f"Slide #{self.id}"