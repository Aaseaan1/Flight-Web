from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('user/', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/flights/', views.AdminFlightsView.as_view(), name='admin_flights'),
    path('admin/bookings/', views.AdminBookingsView.as_view(), name='admin_bookings'),
    path('admin/users/', views.AdminUsersView.as_view(), name='admin_users'),
    path('admin/analytics/', views.AdminAnalyticsView.as_view(), name='admin_analytics'),
    path('bookings/', views.UserBookingsView.as_view(), name='user_bookings'),
    path('booking/<str:booking_ref>/', views.BookingDetailView.as_view(), name='booking_detail'),
]
