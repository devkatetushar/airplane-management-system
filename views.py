from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.crypto import get_random_string
from django.db import transaction
from django.db.models import F
from .models import Flight, Booking


def home(request):
    flights = Flight.objects.filter(status="SCHEDULED")
    return render(
        request, "flights/home.html", {"flights": flights}
    )


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(
        passenger=request.user
    ).select_related("flight")

    return render(
        request,
        "flights/my_bookings.html",
        {"bookings": bookings},
    )


@login_required
def book_flight(request, flight_id):
    if request.method != "POST":
        return redirect("home")

    seats = int(request.POST.get("seats", 1))

    if seats < 1 or seats > 10:
        messages.error(request, "Choose between 1 and 10 seats.")
        return redirect("home")

    with transaction.atomic():
        flight = get_object_or_404(
            Flight.objects.select_for_update(),
            pk=flight_id,
            status="SCHEDULED",
        )

        if flight.available_seats < seats:
            messages.error(request, "Not enough seats available.")
            return redirect("home")

        Flight.objects.filter(pk=flight.pk).update(
            available_seats=F("available_seats") - seats
        )

        Booking.objects.create(
            passenger=request.user,
            flight=flight,
            booking_reference=get_random_string(
                12, allowed_chars="ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
            ),
            seats_booked=seats,
        )

    messages.success(request, "Your booking was created.")
    return redirect("my_bookings")





from django.db.models import Sum, F, DecimalField, ExpressionWrapper


@login_required
def mis_dashboard(request):
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    bookings = Booking.objects.filter(ticket_status="BOOKED")

    revenue = bookings.filter(payment_status="PAID").aggregate(
        total=Sum(
            ExpressionWrapper(
                F("flight__ticket_price") * F("seats_booked"),
                output_field=DecimalField(
                    max_digits=12, decimal_places=2
                ),
            )
        )
    )["total"] or 0

    context = {
        "total_flights": Flight.objects.count(),
        "scheduled_flights": Flight.objects.filter(
            status="SCHEDULED"
        ).count(),
        "total_bookings": Booking.objects.count(),
        "total_passengers": Booking.objects.filter(
            ticket_status="BOOKED"
        ).aggregate(total=Sum("seats_booked"))["total"] or 0,
        "cancelled_tickets": Booking.objects.filter(
            ticket_status="CANCELLED"
        ).count(),
        "available_seats": Flight.objects.filter(
            status="SCHEDULED"
        ).aggregate(total=Sum("available_seats"))["total"] or 0,
        "revenue": revenue,
    }

    return render(
        request, "flights/mis_dashboard.html", context
    )
