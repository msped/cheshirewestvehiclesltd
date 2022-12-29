from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import invoice_handler

# Create your views here.

class CreateInvoice(APIView):
    def post(self, request):
        email = invoice_handler(request.data)
        if email:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
