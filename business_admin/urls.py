from django.urls import path

from .views import CreateInvoice, CreateListVehicle, CreateListGalleryItem

urlpatterns = [
    path('invoice/', CreateInvoice.as_view(), name="create_invoice"),
    path('vehicle/', CreateListVehicle.as_view(), name="create_vehicle"),
    path('gallery/', CreateListGalleryItem.as_view(), name="create_gallery_item"),
]
