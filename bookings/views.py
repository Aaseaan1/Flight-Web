from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
from .models import Booking, Passenger, Payment
from flights.models import Flight, Seat

@method_decorator(login_required, name='dispatch')
class BookFlightView(TemplateView):
    template_name = 'bookings/book_flight.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        flight_id = kwargs.get('flight_id')
        flight = get_object_or_404(Flight, id=flight_id)
        
        # Get passengers count from session or default to 1
        passengers = int(self.request.GET.get('passengers', 1))
        
        context.update({
            'flight': flight,
            'passengers': passengers,
            'passenger_range': range(passengers),
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        flight_id = kwargs.get('flight_id')
        flight = get_object_or_404(Flight, id=flight_id)
        
        passengers_count = int(request.POST.get('passengers', 1))
        seat_class = request.POST.get('seat_class', 'economy')
        trip_type = request.POST.get('trip_type', 'one_way')
        
        # Calculate pricing
        if seat_class == 'economy':
            base_price = flight.economy_price
        elif seat_class == 'business':
            base_price = flight.business_price
        else:
            base_price = flight.first_class_price
        
        total_amount = base_price * passengers_count
        taxes = total_amount * Decimal('0.12')  # 12% tax
        service_fee = Decimal('25.00')  # Fixed service fee
        
        # Create booking
        booking = Booking.objects.create(
            user=request.user,
            trip_type=trip_type,
            outbound_flight=flight,
            passengers=passengers_count,
            total_amount=total_amount,
            taxes=taxes,
            service_fee=service_fee,
            contact_email=request.user.email,
            contact_phone=request.POST.get('contact_phone', ''),
        )
        
        # Store passenger info in session for next step
        passenger_data = []
        for i in range(passengers_count):
            passenger_data.append({
                'title': request.POST.get(f'passenger_{i}_title', ''),
                'first_name': request.POST.get(f'passenger_{i}_first_name', ''),
                'last_name': request.POST.get(f'passenger_{i}_last_name', ''),
                'date_of_birth': request.POST.get(f'passenger_{i}_date_of_birth', ''),
                'passport_number': request.POST.get(f'passenger_{i}_passport_number', ''),
                'nationality': request.POST.get(f'passenger_{i}_nationality', ''),
            })
        
        request.session['passenger_data'] = passenger_data
        request.session['booking_reference'] = booking.booking_reference
        
        messages.success(request, f'Booking created successfully! Reference: {booking.booking_reference}')
        return redirect('bookings:passenger_details', booking_ref=booking.booking_reference)

@method_decorator(login_required, name='dispatch')
class PassengerDetailsView(TemplateView):
    template_name = 'bookings/passenger_details.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        booking_ref = kwargs.get('booking_ref')
        booking = get_object_or_404(Booking, booking_reference=booking_ref, user=self.request.user)
        
        # Get passenger data from session
        passenger_data = self.request.session.get('passenger_data', [])
        
        context.update({
            'booking': booking,
            'passenger_data': passenger_data,
            'passenger_range': range(booking.passengers),
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        booking_ref = kwargs.get('booking_ref')
        booking = get_object_or_404(Booking, booking_reference=booking_ref, user=request.user)
        
        # Create passenger records
        for i in range(booking.passengers):
            Passenger.objects.create(
                booking=booking,
                title=request.POST.get(f'passenger_{i}_title', ''),
                first_name=request.POST.get(f'passenger_{i}_first_name', ''),
                last_name=request.POST.get(f'passenger_{i}_last_name', ''),
                date_of_birth=request.POST.get(f'passenger_{i}_date_of_birth') or None,
                passport_number=request.POST.get(f'passenger_{i}_passport_number', ''),
                nationality=request.POST.get(f'passenger_{i}_nationality', ''),
                meal_preference=request.POST.get(f'passenger_{i}_meal_preference', ''),
                special_assistance=request.POST.get(f'passenger_{i}_special_assistance', ''),
            )
        
        return redirect('bookings:seat_selection', booking_ref=booking.booking_reference)

@method_decorator(login_required, name='dispatch')
class SeatSelectionView(TemplateView):
    template_name = 'bookings/seat_selection.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        booking_ref = kwargs.get('booking_ref')
        booking = get_object_or_404(Booking, booking_reference=booking_ref, user=self.request.user)
        
        # Get available seats for the flight
        seats = Seat.objects.filter(
            flight=booking.outbound_flight,
            is_available=True
        ).order_by('seat_number')
        
        passengers = Passenger.objects.filter(booking=booking)
        
        context.update({
            'booking': booking,
            'seats': seats,
            'passengers': passengers,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        booking_ref = kwargs.get('booking_ref')
        booking = get_object_or_404(Booking, booking_reference=booking_ref, user=request.user)
        
        passengers = Passenger.objects.filter(booking=booking)
        
        # Assign seats to passengers
        for i, passenger in enumerate(passengers):
            seat_number = request.POST.get(f'passenger_{i}_seat')
            if seat_number:
                try:
                    seat = Seat.objects.get(
                        flight=booking.outbound_flight,
                        seat_number=seat_number,
                        is_available=True
                    )
                    passenger.outbound_seat = seat
                    passenger.save()
                    
                    # Mark seat as unavailable
                    seat.is_available = False
                    seat.save()
                    
                except Seat.DoesNotExist:
                    messages.error(request, f'Seat {seat_number} is not available.')
                    return redirect('bookings:seat_selection', booking_ref=booking.booking_reference)
        
        return redirect('bookings:payment', booking_ref=booking.booking_reference)

@method_decorator(login_required, name='dispatch')
class PaymentView(TemplateView):
    template_name = 'bookings/payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        booking_ref = kwargs.get('booking_ref')
        booking = get_object_or_404(Booking, booking_reference=booking_ref, user=self.request.user)
        
        context.update({
            'booking': booking,
            'grand_total': booking.get_grand_total(),
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        booking_ref = kwargs.get('booking_ref')
        booking = get_object_or_404(Booking, booking_reference=booking_ref, user=request.user)
        
        payment_method = request.POST.get('payment_method')
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.get_grand_total(),
            payment_method=payment_method,
            status='completed',  # In real app, this would be 'pending' until gateway confirms
            processed_at=timezone.now(),
            transaction_id=f'TXN_{booking.booking_reference}_{timezone.now().strftime("%Y%m%d%H%M%S")}'
        )
        
        # Update booking status
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save()
        
        # Update flight seat availability
        flight = booking.outbound_flight
        flight.available_economy_seats -= booking.passengers
        flight.save()
        
        # Clear session data
        if 'passenger_data' in request.session:
            del request.session['passenger_data']
        if 'booking_reference' in request.session:
            del request.session['booking_reference']
        
        messages.success(request, 'Payment successful! Your booking is confirmed.')
        return redirect('bookings:confirmation', booking_ref=booking.booking_reference)

@method_decorator(login_required, name='dispatch')
class BookingConfirmationView(TemplateView):
    template_name = 'bookings/confirmation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        booking_ref = kwargs.get('booking_ref')
        booking = get_object_or_404(Booking, booking_reference=booking_ref, user=self.request.user)
        
        passengers = Passenger.objects.filter(booking=booking)
        
        try:
            payment = Payment.objects.get(booking=booking)
        except Payment.DoesNotExist:
            payment = None
        
        context.update({
            'booking': booking,
            'passengers': passengers,
            'payment': payment,
        })
        
        return context

@method_decorator(login_required, name='dispatch')
class CancelBookingView(View):
    
    def post(self, request, *args, **kwargs):
        booking_ref = kwargs.get('booking_ref')
        booking = get_object_or_404(Booking, booking_reference=booking_ref, user=request.user)
        
        if booking.status == 'confirmed':
            # Update booking status
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.save()
            
            # Release seats
            passengers = Passenger.objects.filter(booking=booking)
            for passenger in passengers:
                if passenger.outbound_seat:
                    passenger.outbound_seat.is_available = True
                    passenger.outbound_seat.save()
            
            # Update flight availability
            flight = booking.outbound_flight
            flight.available_economy_seats += booking.passengers
            flight.save()
            
            messages.success(request, f'Booking {booking.booking_reference} has been cancelled successfully.')
        else:
            messages.error(request, 'This booking cannot be cancelled.')
        
        return redirect('dashboard:user_bookings')
