import json
import shutil
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import override_settings
from rest_framework.test import APITestCase

from sales.models import VehicleImages, Vehicle

MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestBusinessAdminVehicle(APITestCase):

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

    def update_vehicle_with_images(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        vehicle = Vehicle.objects.get(
            make="BMW",
            model="5 Series",
            trim="M",
            year=2018
        )
        response = self.client.patch(
            f'/api/admin/vehicle/{vehicle.slug}/',
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(VehicleImages.objects.filter(
            vehicle_id=vehicle.id
        ).count(), 4)

    def update_vehicle_without_images(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        vehicle = Vehicle.objects.get(
            make="BMW",
            model="5 Series",
            trim="M",
            year=2018
        )
        response = self.client.patch(
            f'/api/admin/vehicle/{vehicle.slug}/',
            {
                "make": "BMW",
                "model": "3 Series",
                "trim": "M",
                "year": 2018,
                "fuel": "1",
                "body_type": "4",
                "car_state": "2",
                "reserved": "1",
                "mileage": 32500,
                "engine_size": 2998,
                "mot_expiry": "2023-04-11",
                "extras": "Test M3",
                "price": "32500.00",
                "published": True,
                'uploaded_images': []
            },
            format="multipart",
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(VehicleImages.objects.filter(
            vehicle_id=vehicle.id
        ).count(), 4)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['model'], '3 Series')
        self.assertEqual(json_response['mileage'], 32500)
        self.assertEqual(json_response['extras'], 'Test M3')

    def delete_vehicle_image(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        image = VehicleImages.objects.filter(
            vehicle__slug="bmw-3-series-m-2018"
        ).first()
        response = self.client.delete(
            f'/api/admin/vehicle/image/{image.id}/',
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(VehicleImages.objects.filter(
            vehicle_id=image.vehicle.id
        ).count(), 3)

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
            '/api/admin/vehicle/bmw-3-series-m-2018/',
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 204)

    def test_in_order(self):
        self.create_vehicle_no_images()
        self.create_vehicle_with_images()
        self.get_vehicle()
        self.update_vehicle_with_images()
        self.update_vehicle_without_images()
        self.delete_vehicle_image()
        self.delete_vehicle()
