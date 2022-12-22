from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Vehicle
from .serializers import VehicleSerializerList, VehicleSerializer

class ListVehicles(ListAPIView):
    serializer_class = VehicleSerializerList
    queryset = Vehicle.objects.filter(Q(reserved='1') | Q(reserved='2'))
    paginate_by = 10

class VehicleDetail(RetrieveAPIView):
    serializer_class = VehicleSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    queryset = Vehicle.objects.all()
