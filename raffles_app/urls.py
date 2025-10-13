


"""
Rutas principales de la aplicación `raffles_app`.
Define los endpoints de la aplicación: rifas, autenticación, perfil,
carrito, contacto y sistema de recuperación de contraseñas.
"""

from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import wompi_webhook


urlpatterns = [
    # ----------------------------
    #  Sección principal (sitio público)
    # ----------------------------
    path("", views.home, name="home"),  # Página de inicio (hero, banners, etc.)
    path("about/", views.about, name="about"),  # Página "Acerca de"
    path("contact/", views.contact, name="contact"),  # Formulario de contacto

    # ----------------------------
    #  Rifas
    # ----------------------------
    path("raffles/", views.raffle_list, name="raffle_list"),  # Lista de rifas
    path("raffle/<int:raffle_id>/", views.raffle_detail, name="raffle_detail"),  # Detalle de rifa
    path("raffle/<int:raffle_id>/buy/", views.buy_ticket, name="buy_ticket"),  # Comprar ticket
    path("raffle/<int:raffle_id>/ticket/", views.ticket, name="ticket"),  # Ticket generado
    path("winners/", views.winners_view, name="winners"),  # Ganadores

    # ----------------------------
    #  Carrito y pagos
    # ----------------------------
    path("cart/", views.cart, name="cart"),  # Ver carrito
    path("cart/edit/<int:ticket_id>/", views.edit_ticket, name="edit_ticket"),  # Editar ticket del carrito
    path("cart/remove/<int:ticket_id>/", views.remove_ticket, name="remove_ticket"),  # Eliminar ticket
    path("checkout/", views.checkout, name="checkout"),  # Proceso de pago
    path("payment/return/", views.payment_return, name="payment_return"),  # Respuesta de la pasarela
    path("payment/success/", views.payment_success, name="payment_success"),  # Pago exitoso

    # ----------------------------
    #  Autenticación de usuarios
    # ----------------------------
    # ----------------------------
    #  Autenticación de usuarios
    # ----------------------------
    path("signup/", views.signup, name="signup"),  # Registro con QR
    path("activate/", views.activate, name="activate"),  # Activación con código TOTP



    path("accounts/login/", auth_views.LoginView.as_view(
        template_name="raffles/login.html"
    ), name="login"),  # Inicio de sesión
    
    path("accounts/logout/", auth_views.LogoutView.as_view(
        next_page="home"
    ), name="logout"),  # Cierre de sesión

    # ----------------------------
    #  Perfil de usuario
    # ----------------------------
    path("profile/", views.user_profile, name="user_profile"),  # Ver perfil
    path("profile/edit/", views.profile_edit, name="profile_edit"),  # Editar perfil

# =============================
# Recuperación de contraseña vía OTP (sin email)
# =============================
    path("password_reset/", views.password_reset_request, name="password_reset_request"),
    path("password_reset/verify/", views.password_reset_verify, name="password_reset_verify"),
    path("password_reset/confirm/", views.password_reset_confirm, name="password_reset_confirm"),
    path("password_reset/done/", views.password_reset_done, name="password_reset_done"),

# =============================
# Weebhooks 
# =============================
    path("payments/webhook/", wompi_webhook, name="wompi_webhook"),


]


