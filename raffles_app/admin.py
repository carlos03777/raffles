from django.contrib import admin
from .models import (
    Profile,
    Motorcycle,
    MotorcycleImage,
    Raffle,
    Ticket,
    CarouselSlide,
)


from django.contrib import admin
from django.utils.html import format_html

# Personaliza el encabezado del admin (parte superior del panel)
admin.site.site_header = format_html(
    '<img src="/static/img/logo.png" height="40" alt="Logo"> Mi Panel'
)

# Personaliza el título de la pestaña del navegador
admin.site.site_title = "Administración"

# Título del dashboard principal
admin.site.index_title = "Bienvenido al panel de control"



# ==============================================================
# ---------------------- Profile Admin -------------------------
# ==============================================================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Administración del perfil de usuario."""
    list_display = ("user", "phone", "city", "document_id")
    search_fields = ("user__username", "phone", "city", "document_id")
    list_filter = ("city",)


# ==============================================================
# -------------------- Motorcycle Admin ------------------------
# ==============================================================

class MotorcycleImageInline(admin.TabularInline):
    """Permite gestionar imágenes de motos directamente desde el admin."""
    model = MotorcycleImage
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        """
        Deshabilita la edición del campo 'is_hologram' en imágenes
        cuando ya existe una imagen holográfica asignada.
        """
        formset = super().get_formset(request, obj, **kwargs)

        if obj:  # Solo aplica cuando se edita una moto existente
            hologram_exists = obj.images.filter(is_hologram=True).exists()

            if hologram_exists:
                original_add_fields = formset.add_fields

                def add_fields(formset_self, form, index):
                    original_add_fields(formset_self, form, index)
                    instance = form.instance
                    if not instance.is_hologram:
                        form.fields["is_hologram"].disabled = True

                formset.add_fields = add_fields

        return formset


@admin.register(Motorcycle)
class MotorcycleAdmin(admin.ModelAdmin):
    """Configuración de administración para motos."""
    list_display = ("brand", "model", "year", "is_new", "mileage", "condition")
    list_filter = ("is_new", "condition", "brand", "year")
    search_fields = ("brand", "model", "year")
    inlines = [MotorcycleImageInline]


# ==============================================================
# ---------------------- Raffle Admin --------------------------
# ==============================================================

class TicketInline(admin.TabularInline):
    """Inline para mostrar los tickets dentro de una rifa."""
    model = Ticket
    extra = 1
    readonly_fields = ("code", "created_at")

    def has_add_permission(self, request, obj=None):
        """Bloquea agregar tickets si la rifa no está 'open'."""
        if obj and getattr(obj, "status", None) != "open":
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        """Bloquea editar tickets si la rifa no está 'open'."""
        if obj and getattr(obj, "status", None) != "open":
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Bloquea eliminar tickets si la rifa no está 'open'."""
        if obj and getattr(obj, "status", None) != "open":
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Raffle)
class RaffleAdmin(admin.ModelAdmin):
    """Administración de rifas."""
    list_display = ("motorcycle", "ticket_price", "max_tickets", "status", "ends_at", "winner_user")
    list_filter = ("status", "created_at", "ends_at")
    search_fields = ("motorcycle__brand", "motorcycle__model")
    inlines = [TicketInline]
    readonly_fields = ("seed_commitment", "seed_reveal", "winner_ticket")

    def get_readonly_fields(self, request, obj=None):
        """Bloquea edición completa si la rifa no está abierta."""
        if obj and obj.status != "open":
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Bloquea eliminar rifas cerradas o terminadas."""
        if obj and obj.status != "open":
            return False
        return super().has_delete_permission(request, obj)


# ==============================================================
# ---------------------- Ticket Admin --------------------------
# ==============================================================

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Administración de tickets."""
    list_display = ("raffle", "number", "user", "payment_status", "raffle_status", "created_at")
    list_filter = ("payment_status", "raffle__status")
    search_fields = ("user__username", "raffle__motorcycle__brand", "raffle__motorcycle__model")
    readonly_fields = ("code", "created_at", "number", "user", "raffle")

    def raffle_status(self, obj):
        """Muestra el estado de la rifa asociada."""
        return obj.raffle.status
    raffle_status.short_description = "Estado de la rifa"

    def has_delete_permission(self, request, obj=None):
        """No permite eliminar tickets pagados o de rifas cerradas."""
        if obj:
            if obj.payment_status == "paid" or (obj.raffle and obj.raffle.status != "open"):
                return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        """Vuelve el ticket de solo lectura si está pagado o rifa no 'open'."""
        if obj:
            if obj.payment_status == "paid" or (obj.raffle and obj.raffle.status != "open"):
                return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_add_permission(self, request):
        """Evita agregar tickets a rifas cerradas vía ?raffle=<id>."""
        raffle_id = request.GET.get("raffle")
        if raffle_id:
            try:
                raffle = Raffle.objects.get(pk=raffle_id)
            except Raffle.DoesNotExist:
                raffle = None
            if raffle and raffle.status != "open":
                return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        """Bloquea editar tickets pagados o de rifas no abiertas."""
        if obj:
            if obj.payment_status == "paid" or (obj.raffle and obj.raffle.status != "open"):
                return False
        return super().has_change_permission(request, obj)


# ==============================================================
# ------------------ Carousel Slide Admin ----------------------
# ==============================================================

@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    """Administración del carrusel de imágenes del home."""
    list_display = ("title", "subtitle", "order", "is_active", "created_at")
    list_editable = ("order", "is_active")
    search_fields = ("title", "subtitle")
    list_filter = ("is_active", "created_at")
    ordering = ("order",)
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Contenido", {
            "fields": ("title", "subtitle", "image", "link"),
        }),
        ("Configuración", {
            "fields": ("order", "is_active", "created_at"),
        }),
    )
