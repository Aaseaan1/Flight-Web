from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Count, Sum, Q
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from .models import UserActivity, SystemNotification, AdminLog
from bookings.models import Booking, Payment
from flights.models import Flight
from core.models import Airport, Airline

@method_decorator(login_required, name='dispatch')
class UserDashboardView(TemplateView):
    template_name = 'dashboard/user_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        
        # Get user's bookings
        recent_bookings = Booking.objects.filter(user=user).order_by('-booked_at')[:5]
        total_bookings = Booking.objects.filter(user=user).count()
        confirmed_bookings = Booking.objects.filter(user=user, status='confirmed').count()
        
        # Get upcoming flights
        upcoming_bookings = Booking.objects.filter(
            user=user,
            status='confirmed',
            outbound_flight__departure_time__gte=datetime.now()
        ).order_by('outbound_flight__departure_time')[:3]
        
        # Get user activities
        recent_activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:10]
        
        # Get notifications
        notifications = SystemNotification.objects.filter(
            Q(is_global=True) | Q(target_users=user),
            is_read=False
        ).order_by('-created_at')[:5]
        
        context.update({
            'recent_bookings': recent_bookings,
            'total_bookings': total_bookings,
            'confirmed_bookings': confirmed_bookings,
            'upcoming_bookings': upcoming_bookings,
            'recent_activities': recent_activities,
            'notifications': notifications,
        })
        
        return context

@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = 'dashboard/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate statistics
        total_users = User.objects.count()
        total_bookings = Booking.objects.count()
        total_flights = Flight.objects.count()
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Recent bookings
        recent_bookings = Booking.objects.select_related(
            'user', 'outbound_flight'
        ).order_by('-booked_at')[:10]
        
        # Popular destinations
        popular_destinations = Airport.objects.annotate(
            booking_count=Count('arriving_flights__outbound_bookings')
        ).order_by('-booking_count')[:5]
        
        # Revenue by month (last 6 months)
        from django.db.models import TruncMonth
        monthly_revenue = Payment.objects.filter(
            status='completed',
            created_at__gte=datetime.now() - timedelta(days=180)
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        # Admin logs
        recent_logs = AdminLog.objects.select_related('admin_user').order_by('-created_at')[:10]
        
        context.update({
            'total_users': total_users,
            'total_bookings': total_bookings,
            'total_flights': total_flights,
            'total_revenue': total_revenue,
            'recent_bookings': recent_bookings,
            'popular_destinations': popular_destinations,
            'monthly_revenue': monthly_revenue,
            'recent_logs': recent_logs,
        })
        
        return context

@method_decorator(staff_member_required, name='dispatch')
class AdminFlightsView(TemplateView):
    template_name = 'dashboard/admin_flights.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all flights with related data
        flights = Flight.objects.select_related(
            'airline', 'origin', 'destination', 'aircraft'
        ).order_by('-departure_time')[:50]
        
        # Flight statistics
        total_flights = Flight.objects.count()
        scheduled_flights = Flight.objects.filter(status='scheduled').count()
        completed_flights = Flight.objects.filter(status='landed').count()
        cancelled_flights = Flight.objects.filter(status='cancelled').count()
        
        context.update({
            'flights': flights,
            'total_flights': total_flights,
            'scheduled_flights': scheduled_flights,
            'completed_flights': completed_flights,
            'cancelled_flights': cancelled_flights,
        })
        
        return context

@method_decorator(staff_member_required, name='dispatch')
class AdminBookingsView(TemplateView):
    template_name = 'dashboard/admin_bookings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all bookings with related data
        bookings = Booking.objects.select_related(
            'user', 'outbound_flight__airline', 'outbound_flight__origin', 'outbound_flight__destination'
        ).order_by('-booked_at')[:100]
        
        # Booking statistics
        total_bookings = Booking.objects.count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        cancelled_bookings = Booking.objects.filter(status='cancelled').count()
        
        context.update({
            'bookings': bookings,
            'total_bookings': total_bookings,
            'confirmed_bookings': confirmed_bookings,
            'pending_bookings': pending_bookings,
            'cancelled_bookings': cancelled_bookings,
        })
        
        return context

@method_decorator(staff_member_required, name='dispatch')
class AdminUsersView(TemplateView):
    template_name = 'dashboard/admin_users.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all users with related data
        users = User.objects.select_related('userprofile').order_by('-date_joined')[:100]
        
        # User statistics
        total_users = User.objects.count()
        verified_users = User.objects.filter(userprofile__email_verified=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        active_users = User.objects.filter(is_active=True).count()
        
        context.update({
            'users': users,
            'total_users': total_users,
            'verified_users': verified_users,
            'staff_users': staff_users,
            'active_users': active_users,
        })
        
        return context

@method_decorator(staff_member_required, name='dispatch')
class AdminAnalyticsView(TemplateView):
    template_name = 'dashboard/admin_analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Revenue analytics
        from django.db.models import TruncDay, TruncWeek, TruncMonth
        
        # Daily revenue (last 30 days)
        daily_revenue = Payment.objects.filter(
            status='completed',
            created_at__gte=datetime.now() - timedelta(days=30)
        ).annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            total=Sum('amount')
        ).order_by('day')
        
        # Weekly revenue (last 12 weeks)
        weekly_revenue = Payment.objects.filter(
            status='completed',
            created_at__gte=datetime.now() - timedelta(weeks=12)
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            total=Sum('amount')
        ).order_by('week')
        
        # Top routes
        top_routes = Booking.objects.filter(
            status='confirmed'
        ).values(
            'outbound_flight__origin__code',
            'outbound_flight__destination__code'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Airline performance
        airline_performance = Airline.objects.annotate(
            booking_count=Count('flight__outbound_bookings'),
            revenue=Sum('flight__outbound_bookings__total_amount')
        ).order_by('-booking_count')[:10]
        
        context.update({
            'daily_revenue': daily_revenue,
            'weekly_revenue': weekly_revenue,
            'top_routes': top_routes,
            'airline_performance': airline_performance,
        })
        
        return context

@method_decorator(login_required, name='dispatch')
class UserBookingsView(TemplateView):
    template_name = 'dashboard/user_bookings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's bookings
        bookings = Booking.objects.filter(user=self.request.user).select_related(
            'outbound_flight__airline', 'outbound_flight__origin', 'outbound_flight__destination'
        ).order_by('-booked_at')
        
        context['bookings'] = bookings
        
        return context

@method_decorator(login_required, name='dispatch')
class BookingDetailView(TemplateView):
    template_name = 'dashboard/booking_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        booking_ref = kwargs.get('booking_ref')
        booking = get_object_or_404(
            Booking,
            booking_reference=booking_ref,
            user=self.request.user
        )
        
        # Get passengers
        passengers = booking.passenger_details.all()
        
        # Get payment
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
