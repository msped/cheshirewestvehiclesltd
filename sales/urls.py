from django.urls import path

from .views import ListVehicles, VehicleDetail

urlpatterns = [
    path('', ListVehicles.as_view(), name="list_of_vehicles"),
    path('<str:slug>/', VehicleDetail.as_view(), name="vehicle_detail"),
]
