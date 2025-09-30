from django.contrib.auth import views as auth_views

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Página de inicio con hero
    path("raffles/", views.raffle_list, name="raffle_list"),  # Lista de rifas
    path("raffle/<int:raffle_id>/", views.raffle_detail, name="raffle_detail"),  # Detalle
    path("raffle/<int:raffle_id>/buy/", views.buy_ticket, name="buy_ticket"),  # Comprar ticket
    
    path("raffle/<int:raffle_id>/ticket/", views.ticket, name="ticket"),
    path("signup/", views.signup, name="signup"),
       # login y logout
    # path("login/", auth_views.LoginView.as_view(template_name="templates/raffles/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="raffles/login.html"), name="login"),

    path("profile/", views.user_profile, name="user_profile"),  # Perfil
    path("about/", views.about, name="about"),  # ✅ nueva ruta
    path("cart/", views.cart, name="cart"),  # ✅ nueva ruta
    path("cart/remove/<int:ticket_id>/", views.remove_ticket, name="remove_ticket"),
    path("cart/edit/<int:ticket_id>/", views.edit_ticket, name="edit_ticket"),
    path("raffle/<int:raffle_id>/buy/", views.buy_ticket, name="buy_ticket"),

    path("contact/", views.contact, name="contact"),  # ✅ nueva ruta
    path("ticket/", views.ticket, name="ticket"),  # ✅ nueva ruta

    path("password_reset/", auth_views.PasswordResetView.as_view(template_name="raffles/password_reset.html"),   name="password_reset"),

    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="raffles/password_reset_done.html"), name="password_reset_done"),

    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="raffles/password_reset_confirm.html"), name="password_reset_confirm"),

    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="raffles/password_reset_complete.html"), name="password_reset_complete"),


]
