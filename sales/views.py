import os
import stripe
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import Vehicle, Reservation, TradeIn
from .serializers import (VehicleSerializer, VehicleStateSerializer,
                          ReserveVehicleSerializer, TradeInSerializer)
from .utils import get_reservation_amount, send_reservation_email, send_new_reservation_email

stripe.api_key = os.environ.get('STRIPE_SECRET')


class ListVehicles(ListAPIView):
    serializer_class = VehicleSerializer
    paginate_by = 10

    def get_queryset(self):
        queryset = Vehicle.objects.filter(
            Q(reserved='1') | Q(reserved='2'),
            published=True
        )
        return queryset


class VehicleDetail(RetrieveAPIView):
    serializer_class = VehicleSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = Vehicle.objects.filter(published=True)
        return queryset


class VehicleState(RetrieveAPIView):
    serializer_class = VehicleStateSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = Vehicle.objects.filter(reserved="1", published=True)
        return queryset


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
        reservation = get_object_or_404(Reservation, order_id=reservation_id)
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

            if not vehicle.is_for_sale():
                return Response(
                    {'error': "Vehicle is not for sale therefore can't be reserved."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            resvervations_data = request.data.copy()
            tradein_data = resvervations_data.pop('tradein', None)
            reservation_serializer = ReserveVehicleSerializer(
                data=request.data, many=False)
            reservation_serializer.is_valid(raise_exception=True)
            reservation = reservation_serializer.save(vehicle=vehicle)

            if tradein_data:
                tradein_serializer = TradeInSerializer(
                    data=tradein_data, many=False)
                tradein_serializer.is_valid(raise_exception=True)
                tradein_serializer.save(reservation=reservation)

            intent = stripe.PaymentIntent.create(
                currency='gbp',
                amount=get_reservation_amount(),
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

        except stripe.error.StripeError as error:
            return Response(
                {'error': str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )
