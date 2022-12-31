from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from sales.models import Vehicle
from sales.serializers import (
    VehicleSerializer
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
    queryset = queryset = Vehicle.objects.all()
    pagination_by = 10
    serializer_class = VehicleSerializer
    permission_classes = [IsAdminUser]
