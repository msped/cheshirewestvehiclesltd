from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Vehicle
from .serializers import VehicleSerializer, VehicleStateSerializer

class ListVehicles(ListAPIView):
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.filter(Q(reserved='1') | Q(reserved='2'))
    paginate_by = 10

class VehicleDetail(RetrieveAPIView):
    serializer_class = VehicleSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    queryset = Vehicle.objects.all()

class VehicleState(RetrieveAPIView):
    serializer_class = VehicleStateSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'vehicle_id'
    queryset = Vehicle.objects.filter(reserved="1")
