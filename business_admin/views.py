from rest_framework import status
from rest_framework.generics import (
    DestroyAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from gallery.models import GalleryItem, GalleryImage
from gallery.serializers import GallerySerializer, GalleryImageSerializer
from sales.models import Vehicle, VehicleImages
from sales.serializers import (
    VehicleSerializer,
    VehicleImagesSerializer
)
from .utils import invoice_handler

# Create your views here.

class CreateInvoice(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        email = invoice_handler(request.data)
        if email:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateListVehicle(ListCreateAPIView):
    queryset = Vehicle.objects.all()
    pagination_by = 10
    serializer_class = VehicleSerializer
    permission_classes = [IsAdminUser]

class CreateListGalleryItem(ListCreateAPIView):
    queryset = GalleryItem.objects.all()
    pagination_class = 10
    serializer_class = GallerySerializer
    permission_classes = [IsAdminUser]

class GetUpdateDeleteVehicle(RetrieveUpdateDestroyAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [IsAdminUser]
    queryset = Vehicle.objects.all()
    lookup_field = "slug"

class GetUpdateDeleteGallery(RetrieveUpdateDestroyAPIView):
    serializer_class = GallerySerializer
    permission_classes = [IsAdminUser]
    queryset = GalleryItem.objects.all()
    lookup_field = "slug"

class DeleteVehicleImage(DestroyAPIView):
    serializer_class = VehicleImagesSerializer
    permission_classes = [IsAdminUser]
    queryset = VehicleImages.objects.all()
    lookup_url_kwarg = 'object_id'

class DeleteGalleryImage(DestroyAPIView):
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAdminUser]
    queryset = GalleryImage.objects.all()
    lookup_url_kwarg = 'object_id'
