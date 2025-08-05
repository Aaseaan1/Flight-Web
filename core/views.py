from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Newsletter, Airport, Airline
from flights.models import Flight
from django.db.models import Q
from datetime import datetime, timedelta

class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get popular destinations (top 6 airports by flight count)
        popular_destinations = Airport.objects.filter(
            arriving_flights__departure_time__gte=datetime.now()
        ).distinct()[:6]
        
        # Get featured airlines
        featured_airlines = Airline.objects.all()[:4]
        
        # Get upcoming flights for showcase
        upcoming_flights = Flight.objects.filter(
            departure_time__gte=datetime.now(),
            status='scheduled'
        ).select_related('airline', 'origin', 'destination')[:3]
        
        context.update({
            'popular_destinations': popular_destinations,
            'featured_airlines': featured_airlines,
            'upcoming_flights': upcoming_flights,
        })
        
        return context

class AboutView(TemplateView):
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add statistics
        context.update({
            'total_flights': Flight.objects.count(),
            'total_destinations': Airport.objects.count(),
            'partner_airlines': Airline.objects.count(),
            'happy_customers': 50000,  # This could be calculated from bookings
        })
        
        return context

class ContactView(TemplateView):
    template_name = 'core/contact.html'
    
    def post(self, request, *args, **kwargs):
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if all([name, email, subject, message]):
            # In a real application, you would send an email or save to database
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('core:contact')
        else:
            messages.error(request, 'Please fill in all required fields.')
            return self.get(request, *args, **kwargs)

class DestinationsView(TemplateView):
    template_name = 'core/destinations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all destinations with flights
        destinations = Airport.objects.filter(
            arriving_flights__departure_time__gte=datetime.now()
        ).distinct().order_by('city')
        
        # Group by country
        destinations_by_country = {}
        for destination in destinations:
            country = destination.country
            if country not in destinations_by_country:
                destinations_by_country[country] = []
            destinations_by_country[country].append(destination)
        
        context['destinations_by_country'] = destinations_by_country
        
        return context

class NewsletterSubscribeView(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        # Check if email already exists
        if Newsletter.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False, 
                'message': 'This email is already subscribed'
            })
        
        try:
            Newsletter.objects.create(email=email)
            return JsonResponse({
                'success': True, 
                'message': 'Successfully subscribed to newsletter!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': 'An error occurred. Please try again.'
            })

class SearchAirportsView(View):
    """AJAX view for airport search suggestions"""
    
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'airports': []})
        
        airports = Airport.objects.filter(
            Q(code__icontains=query) |
            Q(name__icontains=query) |
            Q(city__icontains=query)
        )[:10]
        
        results = []
        for airport in airports:
            results.append({
                'code': airport.code,
                'name': airport.name,
                'city': airport.city,
                'country': airport.country,
                'display': f"{airport.code} - {airport.name}, {airport.city}"
            })
        
        return JsonResponse({'airports': results})
