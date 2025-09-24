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


# ---------------- Ticket ---------------- #
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("raffle", "number", "user", "payment_status", "created_at")
    list_filter = ("payment_status", "raffle__status")
    search_fields = ("user__username", "raffle__motorcycle__brand", "raffle__motorcycle__model")
    readonly_fields = ("code", "created_at")
