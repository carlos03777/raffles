from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Página de inicio con hero
    path("raffles/", views.raffle_list, name="raffle_list"),  # Lista de rifas
    path("raffle/<int:raffle_id>/", views.raffle_detail, name="raffle_detail"),  # Detalle
    path("raffle/<int:raffle_id>/buy/", views.buy_ticket, name="buy_ticket"),  # Comprar ticket
    path("ticket/<int:ticket_id>/", views.ticket_detail, name="ticket_detail"),  # Ticket
    path("profile/", views.user_profile, name="user_profile"),  # Perfil
    path("about/", views.about, name="about"),  # ✅ nueva ruta
    path("cart/", views.cart, name="cart"),  # ✅ nueva ruta
    path("contact/", views.contact, name="contact"),  # ✅ nueva ruta
    path("ticket/", views.ticket, name="ticket"),  # ✅ nueva ruta
]
