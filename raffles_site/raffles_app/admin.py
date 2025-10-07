from django.contrib import admin
from .models import Profile, Motorcycle, MotorcycleImage, Raffle, Ticket


# ---------------- Profile ---------------- #
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "city", "document_id")
    search_fields = ("user__username", "phone", "city", "document_id")
    list_filter = ("city",)


# ---------------- Motorcycle ---------------- #
from django.contrib import admin
from .models import Motorcycle, MotorcycleImage


class MotorcycleImageInline(admin.TabularInline):
    model = MotorcycleImage
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if obj:  # solo aplica cuando se edita una moto existente
            hologram_exists = obj.images.filter(is_hologram=True).exists()

            if hologram_exists:
                original_add_fields = formset.add_fields

                def add_fields(formset_self, form, index):
                    original_add_fields(formset_self, form, index)
                    instance = form.instance
                    # Desactivar el checkbox si no es la imagen holográfica actual
                    if not instance.is_hologram:
                        form.fields['is_hologram'].disabled = True

                formset.add_fields = add_fields

        return formset


@admin.register(Motorcycle)
class MotorcycleAdmin(admin.ModelAdmin):
    list_display = ("brand", "model", "year", "is_new", "mileage", "condition")
    list_filter = ("is_new", "condition", "brand", "year")
    search_fields = ("brand", "model", "year")
    inlines = [MotorcycleImageInline]


    


# ---------------- Raffle ---------------- #
# class TicketInline(admin.TabularInline):
#     model = Ticket
#     extra = 1
#     readonly_fields = ("code", "created_at")


# @admin.register(Raffle)
# class RaffleAdmin(admin.ModelAdmin):
#     list_display = ("motorcycle", "ticket_price", "max_tickets", "status", "ends_at", "winner_user")
#     list_filter = ("status", "created_at", "ends_at")
#     search_fields = ("motorcycle__brand", "motorcycle__model")
#     inlines = [TicketInline]
#     readonly_fields = ("seed_commitment", "seed_reveal", "winner_ticket")

#     def get_readonly_fields(self, request, obj=None):
#         """
#         Si la rifa ya no está 'open', todos los campos quedan solo de lectura.
#         """
#         if obj and obj.status != "open":
#             return [f.name for f in self.model._meta.fields]
#         return super().get_readonly_fields(request, obj)

#     def has_delete_permission(self, request, obj=None):
#         """
#         Bloquear eliminar rifas cerradas o terminadas.
#         """
#         if obj and obj.status != "open":
#             return False
#         return super().has_delete_permission(request, obj)


# ---------------- Ticket inline para Raffle ---------------- #
class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1
    readonly_fields = ("code", "created_at")

    def has_add_permission(self, request, obj=None):
        """
        No permitir agregar tickets desde el inline si la rifa no está 'open'.
        obj es la instancia padre (Raffle) cuando se edita una rifa.
        """
        if obj and getattr(obj, "status", None) != "open":
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        """
        No permitir editar tickets desde el inline si la rifa no está 'open'.
        """
        if obj and getattr(obj, "status", None) != "open":
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        No permitir eliminar tickets desde el inline si la rifa no está 'open'.
        """
        if obj and getattr(obj, "status", None) != "open":
            return False
        return super().has_delete_permission(request, obj)


# ---------------- RaffleAdmin (usa el inline) ---------------- #
@admin.register(Raffle)
class RaffleAdmin(admin.ModelAdmin):
    list_display = ("motorcycle", "ticket_price", "max_tickets", "status", "ends_at", "winner_user")
    list_filter = ("status", "created_at", "ends_at")
    search_fields = ("motorcycle__brand", "motorcycle__model")
    inlines = [TicketInline]
    readonly_fields = ("seed_commitment", "seed_reveal", "winner_ticket")

    def get_readonly_fields(self, request, obj=None):
        """
        Si la rifa ya no está 'open', todos los campos quedan solo de lectura.
        (Esto ya lo tenías; lo mantengo)
        """
        if obj and obj.status != "open":
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        Bloquear eliminar rifas cerradas o terminadas.
        """
        if obj and obj.status != "open":
            return False
        return super().has_delete_permission(request, obj)




# ---------------- Ticket ---------------- #
# ---------------- TicketAdmin ---------------- #
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("raffle", "number", "user", "payment_status", "raffle_status", "created_at")
    list_filter = ("payment_status", "raffle__status")
    search_fields = ("user__username", "raffle__motorcycle__brand", "raffle__motorcycle__model")
    readonly_fields = ("code", "created_at", "number", "user", "raffle")

    def raffle_status(self, obj):
        return obj.raffle.status
    raffle_status.short_description = "Estado de la rifa"

    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar tickets pagados ni tickets cuya rifa no está open
        if obj:
            if obj.payment_status == "paid":
                return False
            if obj.raffle and obj.raffle.status != "open":
                return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        """
        Si el ticket está pagado o la rifa no está open, dejamos todo readonly
        (mostrar sólo, sin permitir cambios).
        """
        if obj:
            if obj.payment_status == "paid" or (obj.raffle and obj.raffle.status != "open"):
                return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_add_permission(self, request):
        """
        Si se intenta añadir un ticket desde la vista global y viene un parámetro
        ?raffle=<id> (posible cuando se invoca desde relación), bloqueamos si la rifa no es open.
        Nota: si no hay 'raffle' en GET, permitimos (pero la validación final de modelo seguirá).
        """
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
        """
        Evitar editar tickets desde la interfaz global si la rifa no está open o el ticket está pagado.
        Dejar solo lectura (get_readonly_fields) en esos casos; devolvemos False si queremos
        bloquear totalmente el acceso al formulario. Aquí devolvemos False para evitar cambios.
        """
        if obj:
            if obj.payment_status == "paid" or (obj.raffle and obj.raffle.status != "open"):
                return False
        return super().has_change_permission(request, obj)







# slider

# ---------------- CarouselSlide ---------------- #
from .models import CarouselSlide


@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle", "order", "is_active", "created_at")
    list_editable = ("order", "is_active")
    search_fields = ("title", "subtitle")
    list_filter = ("is_active", "created_at")
    ordering = ("order",)
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Contenido", {
            "fields": ("title", "subtitle", "image", "link")
        }),
        ("Configuración", {
            "fields": ("order", "is_active", "created_at")
        }),
    )
