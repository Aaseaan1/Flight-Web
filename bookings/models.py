from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from flights.models import Flight, Seat
from decimal import Decimal
import uuid

class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
    ]
    
    TRIP_TYPE_CHOICES = [
        ('one_way', 'One Way'),
        ('round_trip', 'Round Trip'),
    ]
    
    booking_reference = models.CharField(max_length=10, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    
    # Trip details
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPE_CHOICES, default='one_way')
    outbound_flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='outbound_bookings')
    return_flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='return_bookings', null=True, blank=True)
    
    # Passenger details
    passengers = models.PositiveIntegerField(default=1)
    
    # Pricing
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    taxes = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    
    # Timestamps
    booked_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Contact information
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    
    class Meta:
        ordering = ['-booked_at']
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        super().save(*args, **kwargs)
    
    def generate_booking_reference(self):
        """Generate a unique 6-character booking reference"""
        import random
        import string
        while True:
            ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Booking.objects.filter(booking_reference=ref).exists():
                return ref
    
    def __str__(self):
        return f"Booking {self.booking_reference} - {self.user.username}"
    
    def get_grand_total(self):
        return self.total_amount + self.taxes + self.service_fee

class Passenger(models.Model):
    TITLE_CHOICES = [
        ('mr', 'Mr.'),
        ('mrs', 'Mrs.'),
        ('ms', 'Ms.'),
        ('dr', 'Dr.'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passenger_details')
    
    # Personal information
    title = models.CharField(max_length=5, choices=TITLE_CHOICES)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=20, blank=True)
    nationality = models.CharField(max_length=50)
    
    # Flight-specific details
    outbound_seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True, related_name='outbound_passengers')
    return_seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True, related_name='return_passengers')
    
    # Special requirements
    meal_preference = models.CharField(max_length=50, blank=True)
    special_assistance = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_title_display()} {self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('wallet', 'Wallet'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Payment gateway details
    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.booking.booking_reference}"
