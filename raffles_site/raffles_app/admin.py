from django.contrib import admin
from .models import Profile, Motorcycle, MotorcycleImage, Raffle, Ticket


# ---------------- Profile ---------------- #
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "city", "document_id")
    search_fields = ("user__username", "phone", "city", "document_id")
    list_filter = ("city",)


# ---------------- Motorcycle ---------------- #
class MotorcycleImageInline(admin.TabularInline):
    model = MotorcycleImage
    extra = 1


@admin.register(Motorcycle)
class MotorcycleAdmin(admin.ModelAdmin):
    list_display = ("brand", "model", "year", "is_new", "mileage", "condition")
    list_filter = ("is_new", "condition", "brand", "year")
    search_fields = ("brand", "model", "year")
    inlines = [MotorcycleImageInline]


# ---------------- Raffle ---------------- #
class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1
    readonly_fields = ("code", "created_at")


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
        if obj and obj.payment_status == "paid":
            return False
        return super().has_delete_permission(request, obj)
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.payment_status == "paid":
            return [f.name for f in self.model._meta.fields]  # todos readonly
        return super().get_readonly_fields(request, obj)






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
