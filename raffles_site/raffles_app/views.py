# ======================================================
# IMPORTS
# ======================================================
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, send_mail
from django.conf import settings

from .models import Raffle, Ticket, CarouselSlide
from .forms import (
    TicketPurchaseForm,
    SignUpForm,
    ProfileForm,
    UserEditForm,
    ProfileEditForm,
    ContactForm,
)
from .tokens import account_activation_token

import hashlib
import requests
import uuid


# ======================================================
# HOME Y LISTADOS
# ======================================================
def home(request):
    """
    Página de inicio con carrusel y rifas abiertas.
    Muestra también los 3 últimos ganadores.
    """
    slides = CarouselSlide.objects.filter(is_active=True).order_by('order')
    raffles = Raffle.objects.filter(status="open")
    last_winners = Raffle.objects.filter(
        status="finished", winner_ticket__isnull=False
    ).order_by("-ends_at")[:3]

    return render(request, "raffles/index.html", {
        "slides": slides,
        "raffles": raffles,
        "last_winners": last_winners,
    })


def raffle_list(request):
    """Listado general de rifas activas."""
    raffles = Raffle.objects.filter(status="open")
    return render(request, "raffles/raffle_list.html", {"raffles": raffles})


def raffle_detail(request, raffle_id):
    """Detalle de una rifa con galería e información del formulario de compra."""
    raffle = get_object_or_404(Raffle, id=raffle_id)
    images = raffle.motorcycle.images.all()
    form = TicketPurchaseForm()
    return render(request, "raffles/raffle_detail.html", {
        "raffle": raffle,
        "images": images,
        "form": form,
    })


def about(request):
    """Página 'Quiénes Somos'."""
    return render(request, "raffles/about.html")


# ======================================================
# AUTENTICACIÓN Y ACTIVACIÓN DE CUENTAS
# ======================================================
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site

def signup(request):
    """
    Registro de usuario con envío de correo de activación.
    El usuario queda inactivo hasta confirmar vía email.
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = "Activa tu cuenta"
            
            # Renderizamos la plantilla HTML
            html_message = render_to_string(
                "raffles/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "protocol": "http",  # o "http" según tu entorno
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            
            # Creamos versión de texto plano (opcional)
            text_message = strip_tags(html_message)
            
            # Enviamos correo con HTML
            email = EmailMultiAlternatives(mail_subject, text_message, to=[form.cleaned_data.get("email")])
            email.attach_alternative(html_message, "text/html")
            email.send()

            return render(request, "raffles/account_activation_sent.html")
    else:
        form = SignUpForm()
    return render(request, "raffles/signup.html", {"form": form})



def activate(request, uidb64, token):
    """Activa una cuenta tras verificar el token recibido por correo."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, "raffles/account_activation_success.html")
    else:
        return render(request, "raffles/account_activation_invalid.html")


# ======================================================
# GANADORES
# ======================================================
def winners_view(request):
    """Muestra todas las rifas con ganador confirmado."""
    raffles = Raffle.objects.filter(winner_ticket__isnull=False).order_by('-created_at')
    return render(request, "raffles/winners.html", {"raffles": raffles})


# ======================================================
# CARRITO Y TICKETS
# ======================================================
@login_required
def cart(request):
    """Muestra los tickets pendientes del usuario logueado."""
    tickets = Ticket.objects.filter(
        user=request.user,
        payment_status="pending",
        raffle__status="open"
    ).select_related("raffle")

    total = tickets.aggregate(total=Sum("raffle__ticket_price"))["total"] or 0

    return render(request, "raffles/cart.html", {
        "tickets": tickets,
        "total": total,
    })


@login_required
def edit_ticket(request, ticket_id):
    """Permite editar el número de un ticket pendiente."""
    ticket = get_object_or_404(
        Ticket, id=ticket_id, user=request.user, payment_status="pending"
    )
    raffle = ticket.raffle

    if request.method == "POST":
        number = request.POST.get("number")
        if not number or not number.isdigit():
            messages.error(request, "Número inválido. Debe ser numérico de 4 dígitos.")
        else:
            try:
                number = int(number)
                # Verificar duplicado en tickets pagados
                if Ticket.objects.filter(
                    raffle=raffle,
                    number=number,
                    payment_status="paid"
                ).exclude(pk=ticket.pk).exists():
                    messages.error(request, f"El número {number} ya está ocupado.")
                else:
                    ticket.number = number
                    ticket.save()
                    messages.success(request, f" Ticket #{ticket.number} actualizado.")
                return redirect("cart")

            except Exception as e:
                messages.error(request, f"Error al actualizar: {e}")

    return render(request, "raffles/ticket.html", {
        "raffle": raffle,
        "ticket": ticket,
        "is_edit": True,
    })


@login_required
def remove_ticket(request, ticket_id):
    """Elimina un ticket pendiente del carrito."""
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user, payment_status="pending")
    if request.method == "POST":
        ticket.delete()
        messages.success(request, f"El ticket #{ticket.number} fue eliminado del carrito.")
    return redirect("cart")


def ticket(request, raffle_id):
    """Vista base para mostrar la información de una boleta antes de comprar."""
    raffle = get_object_or_404(Raffle, id=raffle_id)
    return render(request, "raffles/ticket.html", {"raffle": raffle})


@login_required
def buy_ticket(request, raffle_id):
    """Compra de ticket — permite ingresar o asignar número aleatorio."""
    raffle = get_object_or_404(Raffle, id=raffle_id)

    if request.method == "POST":
        form = TicketPurchaseForm(request.POST)
        if form.is_valid():
            number = form.cleaned_data.get("number")
            try:
                ticket = Ticket.objects.create(
                    raffle=raffle,
                    user=request.user,
                    number=number
                )
                messages.success(request, f"¡Boleta #{ticket.number} agregada al carrito!")
                return redirect("cart")
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Número inválido. Debe ser de 4 dígitos.")
    else:
        form = TicketPurchaseForm()

    return render(request, "raffles/ticket.html", {"raffle": raffle, "form": form})


@login_required
def ticket_detail(request, ticket_id):
    """Detalle de una boleta adquirida."""
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    return render(request, "raffles/ticket_detail.html", {"ticket": ticket})


# ======================================================
# PERFIL DE USUARIO
# ======================================================
@login_required
def user_profile(request):
    """Perfil del usuario: muestra todas las rifas y tickets adquiridos."""
    tickets = Ticket.objects.filter(user=request.user).select_related("raffle")
    return render(request, "raffles/profile.html", {"tickets": tickets})


@login_required
def profile_edit(request):
    """Edición del perfil de usuario y datos complementarios."""
    user = request.user
    profile = user.profile

    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("user_profile")
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileEditForm(instance=profile)

    return render(request, "raffles/profile_edit.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })


# ======================================================
# PAGOS CON WOMPI
# ======================================================
@login_required
def checkout(request):
    """Inicia el proceso de pago con Wompi."""
    tickets = Ticket.objects.filter(user=request.user, payment_status="pending")
    tickets = [t for t in tickets if t.raffle.status != "closed"]

    if not tickets:
        messages.error(request, "No tienes tickets válidos en el carrito.")
        return redirect("cart")

    # Verificar conflictos (boletas ya compradas)
    conflict_tickets = []
    for t in tickets:
        if Ticket.objects.filter(
            raffle=t.raffle,
            number=t.number,
            payment_status="paid"
        ).exclude(user=request.user).exists():
            conflict_tickets.append(str(t.number))

    if conflict_tickets:
        messages.error(request, f"Los siguientes números ya fueron comprados: {', '.join(conflict_tickets)}")
        Ticket.objects.filter(
            user=request.user,
            raffle__in=[t.raffle for t in tickets],
            number__in=conflict_tickets,
            payment_status="pending"
        ).delete()
        return redirect("cart")

    # Calcular total y firma de integridad
    total = sum([float(t.raffle.ticket_price) for t in tickets])
    reference = f"order-{request.user.id}-{uuid.uuid4()}"
    amount_in_cents = int(total * 100)
    currency = "COP"

    integrity_secret = settings.WOMPI_INTEGRITY_SECRET.strip()
    raw_signature = f"{reference}{amount_in_cents}{currency}{integrity_secret}"
    signature = hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()

    Ticket.objects.filter(id__in=[t.id for t in tickets]).update(payment_reference=reference)

    checkout_url = (
        f"https://checkout.wompi.co/p/?"
        f"public-key={settings.WOMPI_PUBLIC_KEY}"
        f"&currency={currency}"
        f"&amount-in-cents={amount_in_cents}"
        f"&reference={reference}"
        f"&redirect-url=http://localhost:8000/payment/return/"
        f"&customer-email={request.user.email}"
        f"&signature:integrity={signature}"
    )

    return redirect(checkout_url)


@login_required
def payment_return(request):
    """Consulta la transacción en Wompi y actualiza el estado de los tickets."""
    transaction_id = request.GET.get("id")
    if not transaction_id:
        messages.error(request, "No se recibió el ID de transacción.")
        return redirect("cart")

    url = f"{settings.WOMPI_BASE_URL}/transactions/{transaction_id}"
    headers = {"Authorization": f"Bearer {settings.WOMPI_PRIVATE_KEY}"}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
    except Exception as e:
        messages.error(request, f"Error al consultar Wompi: {e}")
        return redirect("cart")

    status = data.get("data", {}).get("status", "UNKNOWN")
    reference = data.get("data", {}).get("reference")

    tickets = Ticket.objects.filter(payment_reference=reference, payment_status="pending")

    for ticket in tickets:
        if ticket.raffle.status == "closed":
            ticket.payment_status = "failed"
        else:
            if status == "APPROVED":
                ticket.payment_status = "paid"
            elif status == "DECLINED":
                ticket.payment_status = "failed"
            else:
                ticket.payment_status = "pending"
        ticket.save()

    return redirect(f"/payment/success/?id={transaction_id}&status={status}")


@login_required
def payment_success(request):
    """Muestra el resultado final del pago y actualiza los mensajes."""
    status = request.GET.get("status")
    transaction_id = request.GET.get("id")

    if not transaction_id or not status:
        messages.error(request, "No se pudo verificar el pago.")
        return redirect("cart")

    if status == "APPROVED":
        messages.success(request, " ¡Pago exitoso! Tus tickets ya están activos.")
    elif status == "DECLINED":
        messages.error(request, " El pago fue rechazado.")
    elif status == "PENDING":
        messages.warning(request, " Tu pago está en proceso.")
    else:
        messages.warning(request, f" Estado desconocido: {status}.")

    return redirect("user_profile")


# ======================================================
# CONTACTO
# ======================================================
def contact(request):
    """Página de contacto con envío de correo y limpieza del formulario."""
    sent = False
    form = ContactForm()

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            subject = f"Nuevo mensaje de contacto de {name}"
            full_message = f"De: {name} <{email}>\n\nMensaje:\n{message}"

            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                ["contacto@rifamotos.com"],
                fail_silently=False,
            )

            sent = True
            form = ContactForm()  # limpia después del envío

    return render(request, "raffles/contact.html", {"form": form, "sent": sent})
