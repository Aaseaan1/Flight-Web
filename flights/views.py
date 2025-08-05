from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Flight, Seat
from core.models import Airport

class FlightSearchView(TemplateView):
    template_name = 'flights/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get popular airports for suggestions
        context['popular_airports'] = Airport.objects.all()[:10]
        
        return context

class FlightSearchResultsView(ListView):
    template_name = 'flights/search_results.html'
    context_object_name = 'flights'
    paginate_by = 10
    
    def get_queryset(self):
        departure = self.request.GET.get('departure', '')
        destination = self.request.GET.get('destination', '')
        departure_date = self.request.GET.get('departure_date', '')
        passengers = int(self.request.GET.get('passengers', 1))
        
        queryset = Flight.objects.filter(status='scheduled')
        
        # Filter by departure airport
        if departure:
            queryset = queryset.filter(
                Q(origin__code__icontains=departure) |
                Q(origin__city__icontains=departure) |
                Q(origin__name__icontains=departure)
            )
        
        # Filter by destination airport
        if destination:
            queryset = queryset.filter(
                Q(destination__code__icontains=destination) |
                Q(destination__city__icontains=destination) |
                Q(destination__name__icontains=destination)
            )
        
        # Filter by departure date
        if departure_date:
            try:
                date = datetime.strptime(departure_date, '%Y-%m-%d').date()
                queryset = queryset.filter(departure_time__date=date)
            except ValueError:
                pass
        
        # Filter by available seats
        queryset = queryset.filter(
            available_economy_seats__gte=passengers
        )
        
        # Order by departure time
        queryset = queryset.order_by('departure_time')
        
        return queryset.select_related('airline', 'origin', 'destination', 'aircraft')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pass search parameters to template
        context.update({
            'departure': self.request.GET.get('departure', ''),
            'destination': self.request.GET.get('destination', ''),
            'departure_date': self.request.GET.get('departure_date', ''),
            'passengers': self.request.GET.get('passengers', 1),
            'trip_type': self.request.GET.get('trip_type', 'one_way'),
        })
        
        return context

class FlightDetailView(TemplateView):
    template_name = 'flights/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        flight_id = kwargs.get('flight_id')
        flight = get_object_or_404(Flight, id=flight_id)
        
        # Get seat map
        seats = Seat.objects.filter(flight=flight).order_by('seat_number')
        
        context.update({
            'flight': flight,
            'seats': seats,
        })
        
        return context

class FlightAvailabilityView(TemplateView):
    """AJAX view to check flight availability"""
    
    def get(self, request, *args, **kwargs):
        flight_id = kwargs.get('flight_id')
        passengers = int(request.GET.get('passengers', 1))
        seat_class = request.GET.get('class', 'economy')
        
        try:
            flight = Flight.objects.get(id=flight_id)
            
            if seat_class == 'economy':
                available = flight.available_economy_seats >= passengers
                price = flight.economy_price
            elif seat_class == 'business':
                available = flight.available_business_seats >= passengers
                price = flight.business_price
            elif seat_class == 'first':
                available = flight.available_first_class_seats >= passengers
                price = flight.first_class_price
            else:
                available = False
                price = 0
            
            return JsonResponse({
                'available': available,
                'price': float(price),
                'currency': 'USD',
                'total_price': float(price * passengers)
            })
            
        except Flight.DoesNotExist:
            return JsonResponse({'error': 'Flight not found'}, status=404)
