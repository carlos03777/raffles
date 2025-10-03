from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Raffle, Ticket, CarouselSlide, MotorcycleImage
from .forms import TicketPurchaseForm, ProfileForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignUpForm
from django.db.models import Sum


from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .tokens import account_activation_token


from .models import Raffle, CarouselSlide

def home(request):
    slides = CarouselSlide.objects.filter(is_active=True).order_by('order')
    raffles = Raffle.objects.filter(status="open")
    last_winner = Raffle.objects.filter(status="finished", winner_ticket__isnull=False).order_by("-ends_at").first()
    return render(request, "raffles/index.html", {
        "slides": slides,
        "raffles": raffles,
        "raffle": last_winner,  # 👈 este lo usa la sección de Ganador
    })



def raffle_list(request):
    """Listado de rifas activas."""
    raffles = Raffle.objects.filter(status="open")
    return render(request, "raffles/raffle_list.html", {"raffles": raffles})


def raffle_detail(request, raffle_id):
    """Detalle de una rifa con galería de imágenes."""
    raffle = get_object_or_404(Raffle, id=raffle_id)
    images = raffle.motorcycle.images.all()
    form = TicketPurchaseForm()
    return render(
        request,
        "raffles/raffle_detail.html",
        {"raffle": raffle, "images": images, "form": form},
    )

def about(request):
    """Página 'Quiénes Somos'"""
    return render(request, "raffles/about.html")




def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()          # ✅ ejecuta la lógica completa del form
            user.is_active = False      # 👈 lo desactivamos después
            user.save()

            current_site = get_current_site(request)
            mail_subject = "Activa tu cuenta"
            message = render_to_string(
                "raffles/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            email = EmailMessage(mail_subject, message, to=[form.cleaned_data.get("email")])
            email.send()

            return render(request, "raffles/account_activation_sent.html")
    else:
        form = SignUpForm()
    return render(request, "raffles/signup.html", {"form": form})





from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)  # opcional, lo loguea directo
        return render(request, "raffles/account_activation_success.html")
    else:
        return render(request, "raffles/account_activation_invalid.html")

def winners_view(request):
    # Suponiendo que quieres mostrar el último ganador
    raffle = Raffle.objects.filter(winner_ticket__isnull=False).order_by('-created_at').first()
    return render(request, "raffles/winners.html", {"raffle": raffle})



# @login_required
# def cart(request):
#     """Página del carrito de tickets del usuario autenticado"""
#     tickets = Ticket.objects.filter(user=request.user, payment_status="pending").select_related("raffle")

#     total = tickets.aggregate(
#         total=Sum("raffle__ticket_price")
#     )["total"] or 0

#     return render(request, "raffles/cart.html", {
#         "tickets": tickets,
#         "total": total,
#     })

@login_required
def cart(request):
    """Página del carrito de tickets del usuario autenticado"""
    tickets = Ticket.objects.filter(
        user=request.user,
        payment_status="pending",
        raffle__status="open"   # 👈 filtro agregado
    ).select_related("raffle")

    total = tickets.aggregate(
        total=Sum("raffle__ticket_price")
    )["total"] or 0

    return render(request, "raffles/cart.html", {
        "tickets": tickets,
        "total": total,
    })


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(
        Ticket, id=ticket_id, user=request.user, payment_status="pending"
    )
    raffle = ticket.raffle

    if request.method == "POST":
        number = request.POST.get("number")
        if number and number.isdigit() and len(number) == 4:
            try:
                ticket.number = int(number)  # 👈 aseguramos que sea int
                ticket.save()  # validación: rango y duplicados
                messages.success(request, f"Ticket #{ticket.number} actualizado.")
                return redirect("cart")
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Número inválido. Debe ser de 4 dígitos.")

    return render(
        request,
        "raffles/ticket.html",
        {
            "raffle": raffle,
            "ticket": ticket,
            "is_edit": True,  # 👈 indicador para el template
        },
    )




@login_required
def remove_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user, payment_status="pending")
    if request.method == "POST":
        ticket.delete()
        messages.success(request, f"El ticket #{ticket.number} fue eliminado de tu carrito.")
    return redirect("cart")


def contact(request):
    """Página de contacto"""
    return render(request, "raffles/contact.html")


def ticket(request, raffle_id):
    raffle = get_object_or_404(Raffle, id=raffle_id)
    return render(request, "raffles/ticket.html", {"raffle": raffle})

@login_required
def buy_ticket(request, raffle_id):
    raffle = get_object_or_404(Raffle, id=raffle_id)

    if request.method == "POST":
        form = TicketPurchaseForm(request.POST)
        if form.is_valid():
            number = form.cleaned_data.get("number")  # puede ser None
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

    # 👇 reusar el mismo template de compra de tickets
    return render(request, "raffles/ticket.html", {
        "raffle": raffle,
        "form": form,
    })



@login_required
def ticket_detail(request, ticket_id):
    """Ver detalle de una boleta adquirida."""
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    return render(request, "raffles/ticket_detail.html", {"ticket": ticket})


@login_required
def user_profile(request):
    """Perfil con todas las rifas del usuario."""
    tickets = Ticket.objects.filter(user=request.user).select_related("raffle")
    return render(request, "raffles/profile.html", {"tickets": tickets})




@login_required
def profile_view(request):
    profile = request.user.profile  # el perfil del usuario logueado
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")  # redirige a la misma página
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile.html", {"form": form, "profile": profile})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UserEditForm, ProfileEditForm

@login_required
def profile_edit(request):
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

import hashlib
import requests, uuid
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Ticket


@login_required
def checkout(request):
    # ✅ Tickets pendientes del usuario
    tickets = Ticket.objects.filter(user=request.user, payment_status="pending")

    # ❌ Excluir rifas cerradas o vencidas
    tickets = [t for t in tickets if t.raffle.status != "closed"]

    if not tickets:
        return HttpResponse("No tienes tickets válidos en el carrito.", status=400)

    total = sum([float(t.raffle.ticket_price) for t in tickets])

    # ✅ Generar referencia única
    reference = f"order-{request.user.id}-{uuid.uuid4()}"
    amount_in_cents = int(total * 100)
    currency = "COP"

    # ✅ Generar firma de integridad
    integrity_secret = settings.WOMPI_INTEGRITY_SECRET.strip()
    raw_signature = f"{reference}{amount_in_cents}{currency}{integrity_secret}"
    signature = hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()

    # ✅ Guardar la referencia en los tickets válidos
    Ticket.objects.filter(id__in=[t.id for t in tickets]).update(payment_reference=reference)

    # ✅ URL de checkout Wompi
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
    transaction_id = request.GET.get("id")
    if not transaction_id:
        messages.error(request, "No se recibió el ID de transacción.")
        return redirect("cart")

    # ✅ Consultar transacción en Wompi
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

    # ✅ Tickets asociados
    tickets = Ticket.objects.filter(payment_reference=reference, payment_status="pending")

    for ticket in tickets:
        if ticket.raffle.status == "closed":
            # 🚫 No permitir pagos de rifas cerradas
            ticket.payment_status = "failed"
        else:
            if status == "APPROVED":
                ticket.payment_status = "paid"
            elif status == "DECLINED":
                ticket.payment_status = "failed"
            else:
                ticket.payment_status = "pending"
        ticket.save()

    # Redirigir a success
    return redirect(f"/payment/success/?id={transaction_id}&status={status}")


@login_required
def payment_success(request):
    status = request.GET.get("status")
    transaction_id = request.GET.get("id")

    if not transaction_id or not status:
        messages.error(request, "No se pudo verificar el pago.")
        return redirect("cart")

    # ✅ Mensajes según estado
    if status == "APPROVED":
        messages.success(request, "✅ ¡Pago exitoso! Tus tickets ya están activos.")
    elif status == "DECLINED":
        messages.error(request, "❌ El pago fue rechazado.")
    elif status == "PENDING":
        messages.warning(request, "⏳ Tu pago está en proceso, te notificaremos cuando se confirme.")
    else:
        messages.warning(request, f"⚠️ Estado desconocido: {status}.")

    return redirect("user_profile")
