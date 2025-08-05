from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Airline, Airport
from decimal import Decimal

class Aircraft(models.Model):
    model = models.CharField(max_length=100)  # e.g., Boeing 737-800
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField()
    economy_seats = models.PositiveIntegerField()
    business_seats = models.PositiveIntegerField(default=0)
    first_class_seats = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.airline.name} - {self.model}"

class Flight(models.Model):
    FLIGHT_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('delayed', 'Delayed'),
        ('boarding', 'Boarding'),
        ('departed', 'Departed'),
        ('in_air', 'In Air'),
        ('landed', 'Landed'),
        ('cancelled', 'Cancelled'),
    ]
    
    flight_number = models.CharField(max_length=10)  # e.g., AA123
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departing_flights')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arriving_flights')
    
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    duration = models.DurationField()
    
    economy_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    business_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], default=0)
    first_class_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], default=0)
    
    available_economy_seats = models.PositiveIntegerField()
    available_business_seats = models.PositiveIntegerField(default=0)
    available_first_class_seats = models.PositiveIntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=FLIGHT_STATUS_CHOICES, default='scheduled')
    gate = models.CharField(max_length=10, blank=True)
    terminal = models.CharField(max_length=10, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['flight_number', 'departure_time']
        ordering = ['departure_time']
    
    def __str__(self):
        return f"{self.flight_number} - {self.origin.code} to {self.destination.code}"
    
    def get_total_seats(self):
        return self.aircraft.capacity
    
    def get_available_seats(self):
        return (self.available_economy_seats + 
                self.available_business_seats + 
                self.available_first_class_seats)
    
    def is_available(self):
        return self.get_available_seats() > 0 and self.status == 'scheduled'

class Seat(models.Model):
    SEAT_CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('first', 'First Class'),
    ]
    
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=5)  # e.g., 12A, 3F
    seat_class = models.CharField(max_length=10, choices=SEAT_CLASS_CHOICES)
    is_available = models.BooleanField(default=True)
    is_window = models.BooleanField(default=False)
    is_aisle = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['flight', 'seat_number']
    
    def __str__(self):
        return f"Seat {self.seat_number} - {self.flight.flight_number}"
