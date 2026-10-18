
from django.db import models
from django.contrib.auth.models import User


class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True)
    airline_name = models.CharField(max_length=100)
    airplane_model = models.CharField(max_length=100)

    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)

    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    ticket_price = models.DecimalField(
        max_digits=10, decimal_places=2
    )
    total_seats = models.PositiveIntegerField(default=100)
    available_seats = models.PositiveIntegerField(default=100)

    status = models.CharField(
        max_length=20,
        choices=[
            ("SCHEDULED", "Scheduled"),
            ("DELAYED", "Delayed"),
            ("CANCELLED", "Cancelled"),
            ("COMPLETED", "Completed"),
        ],
        default="SCHEDULED",
    )

    def __str__(self):
        return f"{self.flight_number}: {self.source} to {self.destination}"


class Booking(models.Model):
    passenger = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="flight_bookings",
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.PROTECT,
        related_name="bookings",
    )

    booking_reference = models.CharField(
        max_length=12, unique=True
    )
    seats_booked = models.PositiveIntegerField(default=1)

    booking_date = models.DateTimeField(auto_now_add=True)

    ticket_status = models.CharField(
        max_length=20,
        choices=[
            ("BOOKED", "Booked"),
            ("CANCELLED", "Cancelled"),
            ("COMPLETED", "Completed"),
        ],
        default="BOOKED",
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PAID", "Paid"),
            ("REFUNDED", "Refunded"),
        ],
        default="PENDING",
    )

    def __str__(self):
        return f"{self.booking_reference} - {self.passenger.username}"

    @property
    def total_amount(self):
        return self.flight.ticket_price * self.seats_booked
