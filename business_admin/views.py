import json

from django.contrib.contenttypes.models import ContentType
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import status, filters
from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from auditlog.models import LogEntry

from gallery.models import GalleryItem, GalleryImage
from gallery.serializers import GallerySerializer, GalleryImageSerializer
from sales.models import Vehicle, VehicleImages
from sales.serializers import (
    VehicleSerializer,
    VehicleImagesSerializer
)

from .models import Invoice, Customer
from .serializers import (
    InvoiceSerializer,
    CustomerSerializer,
    CustomerInvoicesSerializer,
    ResendInvoiceSerializer
)
from .utils import invoice_handler

# Create your views here.


class SendInvoice(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, invoice_id):
        email_serializer = ResendInvoiceSerializer(
            data=request.data, many=False)
        if email_serializer.is_valid():
            invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
            invoice_serializer = InvoiceSerializer(invoice, many=False)
            send_email = invoice_handler(
                invoice_serializer.data,
                extra_emails=email_serializer.data
            )
            if send_email:
                LogEntry.objects.create(
                    actor_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(
                        invoice).pk,
                    object_id=invoice.id,
                    object_pk=invoice,
                    object_repr=str(invoice),
                    action=1,  # 1 is update
                    changes=json.dumps({
                        "sent_to": email_serializer.data
                    }),
                )
                return Response(status=status.HTTP_200_OK)
            return Response(
                {"error": "Couldn't render data into PDF file."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(email_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = InvoiceSerializer(data=request.data, many=False)
        if serializer.is_valid():
            serializer.save()
            send_invoice_by_email = invoice_handler(serializer.data)
            if send_invoice_by_email:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"error": "Invoice couldn't be sent."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class InvoiceSearch(ListAPIView):
    permission_classes = [IsAdminUser]
    pagination_by = 10
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'invoice_id',
        'created_date',
        'vrm'
    ]


class RetrieveUpdateDestroyInvoice(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    lookup_field = 'invoice_id'
    lookup_url_kwarg = 'invoice_id'


class CreateListVehicle(ListCreateAPIView):
    queryset = Vehicle.objects.all()
    pagination_by = 10
    serializer_class = VehicleSerializer
    permission_classes = [IsAdminUser]


class CreateListGalleryItem(ListCreateAPIView):
    queryset = GalleryItem.objects.all()
    pagination_by = 10
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


class CustomerSearch(ListAPIView):
    permission_classes = [IsAdminUser]
    pagination_class = None
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'customer_id',
        'first_name',
        'last_name',
        'phone_number',
        'email'
    ]


class CustomerView(RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = "customer_id"
    lookup_url_kwarg = "customer_id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CustomerInvoicesSerializer
        return CustomerSerializer

    def delete(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"error": "Customer object cannot be deleted with Invoice objects still active."},
                status=status.HTTP_400_BAD_REQUEST
            )
