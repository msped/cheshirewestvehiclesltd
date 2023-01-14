from django.urls import path

from .views import (
    CreateInvoice,
    CreateListVehicle,
    CreateListGalleryItem,
    GetUpdateDeleteVehicle
)

urlpatterns = [
    path('invoice/', CreateInvoice.as_view(), name="create_invoice"),
    path('vehicle/', CreateListVehicle.as_view(), name="create_vehicle"),
    path('vehicle/<slug:slug>/', GetUpdateDeleteVehicle.as_view(), name="delete_vehicle"),
    path('gallery/', CreateListGalleryItem.as_view(), name="create_gallery_item"),
]
