from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<int:flight_id>/', views.BookFlightView.as_view(), name='book_flight'),
    path('passenger-details/<str:booking_ref>/', views.PassengerDetailsView.as_view(), name='passenger_details'),
    path('seat-selection/<str:booking_ref>/', views.SeatSelectionView.as_view(), name='seat_selection'),
    path('payment/<str:booking_ref>/', views.PaymentView.as_view(), name='payment'),
    path('confirmation/<str:booking_ref>/', views.BookingConfirmationView.as_view(), name='confirmation'),
    path('cancel/<str:booking_ref>/', views.CancelBookingView.as_view(), name='cancel_booking'),
]
