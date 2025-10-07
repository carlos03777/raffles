from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import secrets, hashlib, random, uuid
from django.core.exceptions import ValidationError


class Profile(models.Model):
    """
    Perfil extendido para cada usuario.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    document_id = models.CharField(max_length=50, unique=True, blank=True, null=True)  # ✅ único
    


    def __str__(self):
        return self.user.username

    def raffles_participated(self):
        return Raffle.objects.filter(tickets__user=self.user).distinct()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(pre_save, sender=User)
def validate_email_constraints(sender, instance, **kwargs):
    # Unicidad
    if User.objects.filter(email=instance.email).exclude(pk=instance.pk).exists():
        raise ValidationError(f"El email {instance.email} ya está en uso.")

    # Inmutabilidad
    if instance.pk:  # usuario ya existe
        old_email = User.objects.filter(pk=instance.pk).values_list("email", flat=True).first()
        if old_email and old_email != instance.email:
            raise ValidationError("El email no puede modificarse una vez registrado.")
        

from django.db import models
from django.core.exceptions import ValidationError


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

    @property
    def hologram_image(self):
        """
        Devuelve la primera imagen marcada como holograma.
        Si no existe, retorna None.
        """
        return self.images.filter(is_hologram=True).first()


class MotorcycleImage(models.Model):
    """
    Permite asociar múltiples imágenes a una misma moto.
    Una de ellas puede marcarse como holograma.
    """
    motorcycle = models.ForeignKey(
        Motorcycle,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="motos/")
    is_hologram = models.BooleanField(
        default=False,
        help_text="Marcar si esta imagen será usada en el card holográfico."
    )

    def clean(self):
        """
        Valida que solo exista una imagen holograma por moto.
        """
        if self.is_hologram:
            qs = MotorcycleImage.objects.filter(
                motorcycle=self.motorcycle,
                is_hologram=True
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("Ya existe una imagen holográfica para esta moto.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Llama a clean() antes de guardar
        super().save(*args, **kwargs)

    def __str__(self):
        tipo = " (Holograma)" if self.is_hologram else ""
        return f"Imagen de {self.motorcycle.brand} {self.motorcycle.model}{tipo}"
    


class Raffle(models.Model):
    """
    Representa una rifa de una moto específica.
    Maneja la lógica de transparencia con commit-reveal.
    """
    STATUS_CHOICES = [
        ("upcoming", "Proxima"),
        ("open", "Abierta"),
        ("closed", "Cerrada"),
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

    # def pick_winner_commit_reveal(self):
    #     """Selecciona un ganador de manera transparente."""
    #     tickets = list(self.tickets.all())
    #     if not tickets:
    #         return None

    #     if not self.verify_commit():
    #         raise ValueError("Seed reveal no coincide con el commitment.")

    #     digest = hashlib.sha256((self.seed_reveal + str(len(tickets))).encode()).hexdigest()
    #     idx = int(digest, 16) % len(tickets)
    #     winner = tickets[idx]
    #     self.winner_ticket = winner
    #     self.status = "finished"
    #     self.save()
    #     return winner



    def pick_winner_commit_reveal(self):
        """Selecciona un ganador de manera transparente."""
        tickets = list(self.tickets.filter(payment_status="paid"))  # 👈 solo pagados
        if not tickets:
            # No hay participantes -> cerramos sin ganador
            self.status = "closed"
            self.save()
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
        ocupados = self.tickets.filter(payment_status="paid").count()
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
    
    def close_if_expired(self):
        """Cierra la rifa si ya pasó la fecha de finalización."""
        from django.utils import timezone
        now = timezone.now()
        if self.status == "open" and self.ends_at <= now:
        # Si no hay participantes, se cierra sin ganador
            if not self.tickets.exists():
                self.status = "closed"
                self.save()
                return None
            # Si hay participantes, se asigna ganador
            return self.pick_winner_commit_reveal()
        return None



# class Ticket(models.Model):
#     """
#     Representa la boleta comprada por un usuario en una rifa de motos.
#     Puede elegirse manualmente o asignarse de forma aleatoria.
#     """
#     PAYMENT_STATUS = [
#         ("pending", "Pendiente"),
#         ("paid", "Pagado"),
#         ("failed", "Fallido"),
#     ]

#     raffle = models.ForeignKey(
#         Raffle,
#         on_delete=models.CASCADE,
#         related_name="tickets"
#     )
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="tickets"
#     )
#     number = models.PositiveIntegerField(blank=True, null=True, db_index=True)
#     code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Código único
#     payment_status = models.CharField(
#         max_length=20,
#         choices=PAYMENT_STATUS,
#         default="pending",
#         db_index=True
#     )
#     payment_reference = models.CharField(
#     max_length=100,
#     blank=True,
#     null=True,
#     db_index=True
#     )

#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['number']

#     # def save(self, *args, **kwargs):
#     #     """Asignar número aleatorio si no se pasa, validar rango y duplicados."""
#     #     if self.number is None:
#     #         posibles = set(range(1, self.raffle.max_tickets + 1))
#     #         ocupados = set(
#     #             Ticket.objects.filter(raffle=self.raffle).values_list("number", flat=True)
#     #         )
#     #         libres = list(posibles - ocupados)
#     #         if not libres:
#     #             raise ValueError("No quedan boletas disponibles en esta rifa.")
#     #         self.number = random.choice(libres)
#     #     else:
#     #         if self.number < 1 or self.number > self.raffle.max_tickets:
#     #             raise ValueError("El número elegido está fuera del rango permitido.")
#     #         if Ticket.objects.filter(raffle=self.raffle, number=self.number).exists():
#     #             raise ValueError(f"La boleta {self.number} ya está ocupada en esta rifa.")

#     #     super().save(*args, **kwargs)

#     def save(self, *args, **kwargs):
#         """Asignar número aleatorio si no se pasa, validar rango y duplicados."""
#         if self.number is None:
#             posibles = set(range(1, self.raffle.max_tickets + 1))
#             ocupados = set(Ticket.objects.filter(raffle=self.raffle,payment_status="paid").values_list("number", flat=True))

#             libres = list(posibles - ocupados)
#             if not libres:
#                 raise ValueError("No quedan boletas disponibles en esta rifa.")
#             self.number = random.choice(libres)
#         else:
#             if self.number < 1 or self.number > self.raffle.max_tickets:
#                 raise ValueError("El número elegido está fuera del rango permitido.")
#             if Ticket.objects.filter(
#                 raffle=self.raffle,
#                 number=self.number,
#                 payment_status="paid"   # 👈 aquí está el cambio

#             ).exclude(pk=self.pk).exists():
#                 raise ValueError(f"La boleta {self.number} ya está ocupada en esta rifa.")

#         super().save(*args, **kwargs)

#     def delete(self, *args, **kwargs):
#         if self.payment_status == "paid":
#             raise ValueError("No se pueden eliminar tickets que ya fueron pagados.")
#         super().delete(*args, **kwargs)


#     def __str__(self):
#         return f"Boleta {self.number} - {self.user.username} en {self.raffle}"



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
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['number']  # 👈 se eliminó unique_together

    def clean(self):
        """Validar que solo haya un ticket pagado por número y rifa."""
        if self.payment_status == "paid":
            conflict = Ticket.objects.filter(
                raffle=self.raffle,
                number=self.number,
                payment_status="paid"
            ).exclude(pk=self.pk).exists()
            if conflict:
                raise ValidationError(f"El número {self.number} ya fue comprado por otro participante.")

    def save(self, *args, **kwargs):
        """Asignar número aleatorio si no se pasa, validar rango y duplicados."""
        self.full_clean()  # 👈 ejecuta la validación anterior

        if self.number is None:
            posibles = set(range(1, self.raffle.max_tickets + 1))
            ocupados = set(
                Ticket.objects.filter(
                    raffle=self.raffle,
                    payment_status="paid"
                ).values_list("number", flat=True)
            )
            libres = list(posibles - ocupados)
            if not libres:
                raise ValueError("No quedan boletas disponibles en esta rifa.")
            self.number = random.choice(libres)
        else:
            if self.number < 1 or self.number > self.raffle.max_tickets:
                raise ValueError("El número elegido está fuera del rango permitido.")
            if Ticket.objects.filter(
                raffle=self.raffle,
                number=self.number,
                payment_status="paid"
            ).exclude(pk=self.pk).exists():
                raise ValueError(f"La boleta {self.number} ya está ocupada en esta rifa.")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.payment_status == "paid":
            raise ValueError("No se pueden eliminar tickets que ya fueron pagados.")
        super().delete(*args, **kwargs)

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