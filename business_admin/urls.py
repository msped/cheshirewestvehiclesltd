from django.urls import path

from .views import (
    CreateInvoice,
    RetrieveUpdateDestroyInvoice,
    CreateListVehicle,
    CreateListGalleryItem,
    GetUpdateDeleteVehicle,
    GetUpdateDeleteGallery,
    DeleteGalleryImage,
    DeleteVehicleImage
)

urlpatterns = [
    path('invoice/', CreateInvoice.as_view(), name="create_invoice"),
    path('invoice/<str:invoice_id>/', RetrieveUpdateDestroyInvoice.as_view(), name="get_invoice"),
    path('vehicle/', CreateListVehicle.as_view(), name="create_vehicle"),
    path('vehicle/<slug:slug>/', GetUpdateDeleteVehicle.as_view(), name="vehicle_options"),
    path(
        'vehicle/image/<int:object_id>/',
        DeleteVehicleImage.as_view(),
        name="vehicle_image_options"
    ),
    path('gallery/', CreateListGalleryItem.as_view(), name="create_gallery_item"),
    path('gallery/<slug:slug>/', GetUpdateDeleteGallery.as_view(), name="gallery_options"),
    path(
        'gallery/image/<int:object_id>/',
        DeleteGalleryImage.as_view(),
        name="gallery_image_options"
    ),
]
