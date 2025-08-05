from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    path('search/', views.FlightSearchView.as_view(), name='search'),
    path('search/results/', views.FlightSearchResultsView.as_view(), name='search_results'),
    path('detail/<int:flight_id>/', views.FlightDetailView.as_view(), name='detail'),
    path('availability/<int:flight_id>/', views.FlightAvailabilityView.as_view(), name='availability'),
]
