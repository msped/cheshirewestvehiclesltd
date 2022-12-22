from django.urls import path

from .views import GalleryList, GalleryDetail

urlpatterns = [
    path('', GalleryList.as_view(), name="gallery_list"),
    path('<slug:slug>/', GalleryDetail.as_view(), name="gallery_list"),
]
