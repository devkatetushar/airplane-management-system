from django.contrib import admin
from .models import Flight, Booking


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "flight_number",
        "airline_name",
        "source",
        "destination",
        "departure_time",
        "ticket_price",
        "available_seats",
        "status",
    )

    search_fields = (
        "flight_number",
        "airline_name",
        "source",
        "destination",
    )

    list_filter = ("status", "airline_name")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "booking_reference",
        "passenger",
        "flight",
        "seats_booked",
        "ticket_status",
        "payment_status",
        "booking_date",
    )

    search_fields = (
        "booking_reference",
        "passenger__username",
        "flight__flight_number",
    )

    list_filter = ("ticket_status", "payment_status")
