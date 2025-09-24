from django.urls import path
from . import views

urlpatterns = [
    path("", views.raffle_list, name="raffle_list"),  # Página principal con rifas
    path("raffle/<int:raffle_id>/", views.raffle_detail, name="raffle_detail"),  # Detalle de rifa
    path("raffle/<int:raffle_id>/buy/", views.buy_ticket, name="buy_ticket"),  # Comprar ticket
    path("ticket/<int:ticket_id>/", views.ticket_detail, name="ticket_detail"),  # Ver ticket
    path("profile/", views.user_profile, name="user_profile"),  # Perfil de usuario
]
