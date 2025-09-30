from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Raffle, Ticket, CarouselSlide, MotorcycleImage
from .forms import TicketPurchaseForm


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


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignUpForm


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # inicia sesión automáticamente
            messages.success(request, "🎉 Tu cuenta fue creada con éxito")
            return redirect("raffle_list")  # ajusta al nombre de tu home
    else:
        form = SignUpForm()
    return render(request, "raffles/signup.html", {"form": form})



from django.db.models import Sum

@login_required
def cart(request):
    """Página del carrito de tickets del usuario autenticado"""
    tickets = Ticket.objects.filter(user=request.user, payment_status="pending").select_related("raffle")

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
    return render(request, "raffles/user_profile.html", {"tickets": tickets})
