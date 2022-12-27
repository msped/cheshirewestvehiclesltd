import os
import stripe
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import Vehicle, Reservations, TradeIn
from .serializers import VehicleSerializer, VehicleStateSerializer
from .utils import get_reservation_amount, send_reservation_email, send_new_reservation_email

stripe.api_key = os.environ.get('STRIPE_SECRET')

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

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError:
        # Invalid payload
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if event["type"] == "payment_intent.succeeded":
        intent = event['data']['object']
        reservation_id = intent["metadata"]["reservation_id"]
        payment_amount = intent["amount"]

        vehicle = get_object_or_404(Vehicle, id=reservation.vehicle.id)
        vehicle.reserved = "2"
        vehicle.save()
        reservation = get_object_or_404(Reservations, order_id=reservation_id)
        reservation.paid = True
        reservation.paymentIntent_id = intent["id"]
        reservation.save()

        if TradeIn.objects.filter(reservation__order_id=reservation_id).exists():
            tradein = TradeIn.objects.get(reservation__order_id=reservation_id)
            send_reservation_email(
                reservation=reservation,
                res_amount=payment_amount,
                tradein=tradein
            )
        else:
            send_reservation_email(
                reservation=reservation,
                res_amount=payment_amount
            )
        send_new_reservation_email(reservation.vehicle)
    return Response(status=status.HTTP_200_OK)

class StripePaymentIntentReserveVehicle(APIView):
    def post(self, request, vehicle_id):
        try:
            vehicle = get_object_or_404(Vehicle, id=vehicle_id)

            if vehicle.reserved == "1":
                reservation = Reservations()
                reservation.name = request.data.get('reservation_name')
                reservation.email = request.data.get('reservation_email')
                reservation.phone_number = request.data.get('reservation_phone_number')
                reservation.vehicle = vehicle
                reservation.save()

                if (
                    request.data.get('tradein_make') is not None and
                    request.data.get('tradein_model') is not None
                ):
                    tradein = TradeIn()
                    tradein.reservation = reservation
                    tradein.make = request.data.get('tradein_make')
                    tradein.model = request.data.get('tradein_model')
                    tradein.trim = request.data.get('tradein_trim')
                    tradein.year = request.data.get('tradein_year')
                    tradein.mileage = request.data.get('tradein_mileage')
                    tradein.comments = request.data.get('tradein_comments')
                    tradein.save()

                reservation_amount = get_reservation_amount()
                intent = stripe.PaymentIntent.create(
                    currency='gbp',
                    amount=reservation_amount,
                    statement_descriptor='Vehicle reservation',
                    payment_method_types=['card'],
                    metadata={
                        'reservation_id': reservation.order_id
                    }
                )

                return Response(
                    {'client_secret': intent.client_secret},
                    status=status.HTTP_200_OK
                )
            return Response(
                {'error': "Vehicle is not for sale therefore can't be reserved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        except stripe.error.CardError as error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.RateLimitError as error:
            return Response({'error': error}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except stripe.error.InvalidRequestError:
            return Response(
                {'error': 'An invalid request occurred'},
                status=status.HTTP_400_BAD_REQUEST
            )
