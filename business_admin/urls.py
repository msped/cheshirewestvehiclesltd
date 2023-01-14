from django.urls import path

from .views import (
    CreateInvoice,
    CreateListVehicle,
    CreateListGalleryItem,
    GetUpdateDeleteVehicle,
    GetUpdateDeleteGallery,
    DeleteGalleryImage
)

urlpatterns = [
    path('invoice/', CreateInvoice.as_view(), name="create_invoice"),
    path('vehicle/', CreateListVehicle.as_view(), name="create_vehicle"),
    path('vehicle/<slug:slug>/', GetUpdateDeleteVehicle.as_view(), name="vehicle_options"),
    path('gallery/', CreateListGalleryItem.as_view(), name="create_gallery_item"),
    path('gallery/<slug:slug>/', GetUpdateDeleteGallery.as_view(), name="gallery_options"),
    path(
        'gallery/image/<pk>/',
        DeleteGalleryImage.as_view(),
        name="delete_gallery_image"
    ),
]
