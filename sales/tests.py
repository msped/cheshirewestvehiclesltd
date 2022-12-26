import json
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase
from .models import (
    Vehicle,
    VehicleImages,
    Reservations,
    TradeIn,
    ReservationAmount
)

from .utils import get_reservation_amount

MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestView(APITestCase):

    def setUp(self):
        v_1 = Vehicle.objects.create(
            slug="mercedes-a-class-a250",
            make="Mercedes",
            model="A Class",
            trim="A250",
            year=2013,
            fuel="1",
            body_type="2",
            car_state="2",
            reserved="1",
            mileage=73500,
            engine_size=1991,
            mot_expiry="2022-09-01",
            extras="Test",
            price=16110.00
        )
        v_1.save()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_get_list_of_vehicles(self):
        vehicle = Vehicle.objects.get(slug="mercedes-a-class-a250-2013")
        response = self.client.get("/api/sales/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": vehicle.id,
                        "slug": "mercedes-a-class-a250-2013",
                        "make": "Mercedes",
                        "model": "A Class",
                        "trim": "A250",
                        "year": 2013,
                        "fuel": "Petrol",
                        "body_type": "Hatchback",
                        "car_state": "Frontline",
                        "reserved": "For Sale",
                        "mileage": 73500,
                        "engine_size": 1991,
                        "mot_expiry": "2022-09-01",
                        "extras": "Test",
                        "price": "16110.00",
                        "images": []
                    }
                ]
            }
        )

    def test_get_vehicle_detail(self):
        vehicle = Vehicle.objects.get(slug="mercedes-a-class-a250-2013")
        response = self.client.get(f"/api/sales/{vehicle.slug}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {
                "id": vehicle.id,
                "slug": "mercedes-a-class-a250-2013",
                "make": "Mercedes",
                "model": "A Class",
                "trim": "A250",
                "year": 2013,
                "fuel": "Petrol",
                "body_type": "Hatchback",
                "car_state": "Frontline",
                "reserved": "For Sale",
                "mileage": 73500,
                "engine_size": 1991,
                "mot_expiry": "2022-09-01",
                "extras": "Test",
                "price": "16110.00",
                "images": []
            }
        )

    def test_get_vehicle_detail_not_found(self):
        response = self.client.get("/api/sales/test-slug-that-doesnt-work/")
        self.assertEqual(response.status_code, 404)

    def test_check_car_state(self):
        vehicle = Vehicle.objects.get(slug="mercedes-a-class-a250-2013")
        response = self.client.get(f"/api/sales/state/{vehicle.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {
                "id": vehicle.id,
                "reserved": "For Sale"
            }
        )

    def test_check_car_state_not_found(self):
        response = self.client.get("/api/sales/state/99/")
        self.assertEqual(response.status_code, 404)

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestSalesModels(APITestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def vehicle_model(self):
        Vehicle.objects.create(
            make='Mercedes',
            model='190E',
            trim='2.3-16',
            year=1991,
            fuel='1',
            body_type='3',
            car_state='2',
            reserved='1',
            mileage=172000,
            engine_size=2994,
            mot_expiry='1997-03-10',
            extras='A bunch of extras on this car.',
            price=11095.00
        )
        vehicle = Vehicle.objects.get(make='Mercedes', mileage=172000)
        self.assertEqual(
            str(vehicle),
            f'{vehicle.id} Mercedes 190E 2.3-16 - £11095.00'
        )

    def vehicle_images(self):
        vehicle = Vehicle.objects.get(make='Mercedes', mileage=172000)
        VehicleImages.objects.create(
            vehicle=vehicle,
            image=SimpleUploadedFile('test.png', b'testimageofavehicle'),
            order_of_images=1
        ).save()
        vehicle_image = VehicleImages.objects.get(
            vehicle_id=vehicle.id,
            order_of_images=1
        )
        self.assertEqual(
            str(vehicle_image),
            f'{vehicle.id} - {vehicle_image.id}'
        )

    def reservations_model(self):
        vehicle = Vehicle.objects.get(make='Mercedes', mileage=172000)
        Reservations.objects.create(
            name='Matt Edwards',
            email='test@test.com',
            phone_number='07123456789',
            vehicle=vehicle,
            paymentIntent_id='testIdFromStripe'
        ).save()
        reservation = Reservations.objects.get(name="Matt Edwards")
        self.assertEqual(
            str(reservation),
            f'Matt Edwards reserved {vehicle.id} Mercedes 190E 2.3-16 - £11095.00'
        )

    def trade_in_model(self):
        reservation = Reservations.objects.get(name="Matt Edwards")
        TradeIn.objects.create(
            reservation=reservation,
            make='Ford',
            model='Focus',
            trim='Zetec',
            year=2014,
            mileage=28614,
            comments='test comments'
        ).save()
        tradein = TradeIn.objects.get(make='Ford', mileage=28614)
        self.assertEqual(
            str(tradein),
            f'Trade In Vehicle for {reservation.id}'
        )

    def reservation_amount_active(self):
        ReservationAmount.objects.create(
            amount=10000,
            active=True
        ).save()
        reservation = ReservationAmount.objects.get(active=True)
        self.assertEqual(
            str(reservation),
            '£100.00 - Active'
        )

    def reservation_amount_inactive(self):
        ReservationAmount.objects.create(
            amount=15000,
            active=False
        ).save()
        reservation = ReservationAmount.objects.get(active=False)
        self.assertEqual(
            str(reservation),
            '£150.00 - Inactive'
        )

    def test_in_order(self):
        self.vehicle_model()
        self.vehicle_images()
        self.reservations_model()
        self.trade_in_model()
        self.reservation_amount_active()
        self.reservation_amount_inactive()

class TestSalesUtils(APITestCase):

    def test_get_reservation_amount_doesnt_exist(self):
        resveration_amount = get_reservation_amount()
        self.assertEqual(resveration_amount, 10000)

    def test_get_reservation_amount_exists(self):
        ReservationAmount.objects.create(
            amount=150,
            active=True
        ).save()
        resveration_amount = get_reservation_amount()
        self.assertEqual(resveration_amount, 150)
