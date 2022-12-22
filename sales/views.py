from django.db.models import Q
from rest_framework.generics import ListAPIView

from .models import Vehicle
from .serializers import VehicleSerializerList

class ListVehicles(ListAPIView):
    serializer_class = VehicleSerializerList
    queryset = Vehicle.objects.filter(Q(reserved='1') | Q(reserved='2'))
    paginate_by = 10
