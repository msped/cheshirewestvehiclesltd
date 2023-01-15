from django.urls import path

from .views import (
    CreateInvoice,
    CreateListVehicle,
    CreateListGalleryItem,
    GetUpdateDeleteVehicle,
    GetUpdateDeleteGallery,
    CreateDeleteGalleryImage,
    CreateDeleteVehicleImage
)

urlpatterns = [
    path('invoice/', CreateInvoice.as_view(), name="create_invoice"),
    path('vehicle/', CreateListVehicle.as_view(), name="create_vehicle"),
    path('vehicle/<slug:slug>/', GetUpdateDeleteVehicle.as_view(), name="vehicle_options"),
    path(
        'vehicle/image/<int:object_id>/',
        CreateDeleteVehicleImage.as_view(),
        name="vehicle_image_options"
    ),
    path('gallery/', CreateListGalleryItem.as_view(), name="create_gallery_item"),
    path('gallery/<slug:slug>/', GetUpdateDeleteGallery.as_view(), name="gallery_options"),
    path(
        'gallery/image/<int:object_id>/',
        CreateDeleteGalleryImage.as_view(),
        name="gallery_image_options"
    ),
]
