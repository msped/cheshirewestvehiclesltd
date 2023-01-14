import shutil
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status

from gallery.models import GalleryItem, GalleryImage
from sales.models import VehicleImages, Vehicle

# Create your tests here.
MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestBusinessAdmin(APITestCase):

    def setUp(self):
        user = get_user_model()
        user.objects.create(
            first_name= 'Harold',
            last_name= 'Finch',
            username= 'admin',
            password=make_password('TestP455word!'),
            is_staff=True
        ).save()

    def temporary_image(self):
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file, 'jpeg')
        tmp_file.seek(0)
        return tmp_file

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def sending_invoice_by_email(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        response = self.client.post(
            '/api/admin/invoice/',
            {
                "name": "Elizbath Windsor",
                "phone_number": "07123456789",
                "email": "test@example.com",
                "address_line_1": "1 The Mall",
                "address_line_2": "",
                "town_city": "Westminter",
                "county": "London",
                "postcode": "SW1A 1AA",
                "make": "Land Rover",
                "model": "Defender",
                "year": "2021",
                "mileage": 250,
                "vrm": "B16 LIZ",
                "labour-qty": 10,
                "labour-unit": 100,
                "labour-total": 1000,
                "invoice-total": 1500,
                "comments": "Testing sending of pdf email",
                "description-1": "Steering rack",
                "qty-1": 1,
                "unit-1": 500,
                "line-1": 500
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def create_vehicle_no_images(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        response = self.client.post(
            '/api/admin/vehicle/',
            {
                "make": "Ford",
                "model": "Mustang",
                "trim": "GT",
                "year": 2015,
                "fuel": "1",
                "body_type": "1",
                "car_state": "2",
                "reserved": "1",
                "mileage": 42500,
                "engine_size": 4996,
                "mot_expiry": "2023-06-21",
                "extras": "Test Mustang GT",
                "price": "32500.00",
                "uploaded_images": []
            },
            format="multipart",
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 201)

    def create_vehicle_with_images(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        response = self.client.post(
            '/api/admin/vehicle/',
            {
                "make": "BMW",
                "model": "5 Series",
                "trim": "M",
                "year": 2018,
                "fuel": "1",
                "body_type": "4",
                "car_state": "2",
                "reserved": "1",
                "mileage": 28614,
                "engine_size": 2998,
                "mot_expiry": "2023-04-11",
                "extras": "Test M5",
                "price": "32500.00",
                "published": True,
                'uploaded_images': [
                    self.temporary_image(),
                    self.temporary_image()
                ]
            },
            format="multipart",
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 201)
        vehicle = Vehicle.objects.get(
            make="BMW",
            model="5 Series",
            trim="M",
            year=2018,
            mileage=28614
        )
        self.assertEqual(VehicleImages.objects.filter(
            vehicle_id=vehicle.id
        ).count(), 2)

    def get_vehicle(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        response = self.client.get(
            '/api/admin/vehicle/bmw-5-series-m-2018/',
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 200)

    def create_gallery_no_images(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        response = self.client.post(
            '/api/admin/gallery/',
            {
                "make": "Ford",
                "model": "Fiesta",
                "trim": "ST",
                "year": 2019,
                "description": "Test description for Fiesta",
                "published": True,
                "uploaded_images": []
            },
            format="multipart",
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 201)

    def create_gallery_with_images(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        response = self.client.post(
            '/api/admin/gallery/',
            {
                "make": "Nissan",
                "model": "Skyline",
                "trim": "GTR V-spec",
                "year": 2001,
                "description": "Godzilla",
                "published": True,
                "uploaded_images": [
                    self.temporary_image(),
                    self.temporary_image()
                ]
            },
            format="multipart",
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 201)
        gallery = GalleryItem.objects.get(
            make="Nissan",
            model="Skyline",
            trim="GTR V-spec",
            year=2001
        )
        self.assertEqual(GalleryImage.objects.filter(
            item_id=gallery.id
        ).count(), 2)

    def get_gallery(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        response = self.client.get(
            '/api/admin/gallery/ford-fiesta-st-2019/',
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 200)

    def delete_vehicle(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        response = self.client.delete(
            '/api/admin/vehicle/bmw-5-series-m-2018/',
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 204)

    def delete_gallery(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        response = self.client.delete(
            '/api/admin/gallery/ford-fiesta-st-2019/',
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 204)

    def test_in_order(self):
        self.sending_invoice_by_email()
        self.create_vehicle_no_images()
        self.create_vehicle_with_images()
        self.get_vehicle()
        self.create_gallery_no_images()
        self.create_gallery_with_images()
        self.get_gallery()
        self.delete_vehicle()
        self.delete_gallery()
