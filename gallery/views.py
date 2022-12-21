from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import GalleryItem, GalleryImage
from .serializers import GallerySerializer

class GalleryList(ListAPIView):
    serializer_class = GallerySerializer
    paginate_by = 10
    queryset = GalleryItem.objects.filter(published=True)
