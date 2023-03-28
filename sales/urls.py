from django.urls import path

from .views import (
    ListVehicles,
    VehicleDetail,
    VehicleState,
    StripePaymentIntentReserveVehicle,
    stripe_webhook
)

urlpatterns = [
    path('', ListVehicles.as_view(), name="list_of_vehicles"),
    path('<str:slug>/', VehicleDetail.as_view(), name="vehicle_detail"),
    path('state/<str:slug>/', VehicleState.as_view(), name="vehicle_state"),
    path(
        'reserve/<int:vehicle_id>/',
        StripePaymentIntentReserveVehicle.as_view(),
        name="payment_intent_reserve_vehicle"
    ),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
]
