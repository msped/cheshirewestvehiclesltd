from django.urls import path

from .views import CreateInvoice

urlpatterns = [
    path('invoice/', CreateInvoice.as_view(), name="create_invoice"),
]
