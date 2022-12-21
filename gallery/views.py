from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import GalleryItem
from .serializers import GallerySerializer

class GalleryList(ListAPIView):
    serializer_class = GallerySerializer
    paginate_by = 10
    queryset = GalleryItem.objects.filter(published=True)

class GalleryDetail(RetrieveAPIView):
    serializer_class = GallerySerializer
    queryset = GalleryItem.objects.filter(published=True)
    lookup_url_kwarg = 'slug'
    lookup_field = 'slug'
