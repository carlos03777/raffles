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


def cart(request):
    """Página del carrito de tickets"""
    return render(request, "raffles/cart.html")

def contact(request):
    """Página de contacto"""
    return render(request, "raffles/contact.html")


def ticket(request):
    """Página para compra de tickets (versión estática/visual)."""
    return render(request, "raffles/ticket.html")


@login_required
def buy_ticket(request, raffle_id):
    """Compra de boleta (manual o aleatoria)."""
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
                messages.success(request, f"¡Boleta {ticket.number} comprada con éxito!")
                return redirect("ticket_detail", ticket_id=ticket.id)
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = TicketPurchaseForm()

    return render(
        request,
        "raffles/buy_ticket.html",
        {"raffle": raffle, "form": form},
    )


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
