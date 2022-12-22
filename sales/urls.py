from django.urls import path

from .views import ListVehicles

urlpatterns = [
    path('', ListVehicles.as_view(), name="list_of_vehicles"),
]
