import json
import shutil
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import override_settings
from rest_framework.test import APITestCase

from gallery.models import GalleryItem, GalleryImage
from sales.models import VehicleImages, Vehicle
from .models import Customer, InvoiceItem, Invoice
from .serializers import (
    InvoiceItemSerializer,
    InvoiceSerializer,
    CustomerSerializer
)
from .utils import get_customer

MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestInvoiceModelsAndSerializers(APITestCase):

    def setUp(self):
        user = get_user_model()
        user.objects.create(
            first_name= 'Harold',
            last_name= 'Finch',
            username= 'admin',
            password=make_password('TestP455word!'),
            is_staff=True
        ).save()
        Customer.objects.create(
            first_name="Cameron",
            last_name="Fitzgerald",
            phone_number="07123456781",
            email="testCam@example.com",
            address_line_1="10 Webb\'s Lane",
            address_line_2="",
            town_city="Middlewich",
            county="Cheshire",
            postcode="AA1 1AA"
        ).save()
        customer = Customer.objects.get(
            first_name="Cameron",
            last_name="Fitzgerald",
            phone_number="07123456781",
            email="testCam@example.com"
        )
        Invoice.objects.create(
            customer=customer,
            make="Mercedes",
            model="Sprinter",
            trim="2.1 CDI",
            year=2013,
            mileage=72000,
            vrm="DK19 CLX",
            labour_quantity=1,
            labour_unit=25.00,
            labour_total=25.00,
            invoice_total=25.00,
            comments="test"
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def customer_serializer_working(self):
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "phone_number": "07123456788",
            "email": "testJane@example.com",
            "address_line_1": "1 Webb\'s Lane",
            "address_line_2": "",
            "town_city": "Middlewich",
            "county": "Cheshire",
            "postcode": "AA1 1AA"
        }
        serializer = CustomerSerializer(data=data, many=False)
        self.assertTrue(serializer.is_valid())

    def invoice_item_serializer_working(self):
        data = {
            "invoice": 1,
            "description": "Test",
            "quantity": 1,
            "unit_price": 25.00
        }
        serializer = InvoiceItemSerializer(data=data, many=False)
        self.assertTrue(serializer.is_valid())

    def invoice_serializer_working(self):
        data = {
            "customer": {
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "07123456789",
                "email": "testJohn@example.com",
                "address_line_1": "1 Webb\'s Lane",
                "address_line_2": "",
                "town_city": "Middlewich",
                "county": "Cheshire",
                "postcode": "AA1 1AA"
            },
            "make": "Ford",
            "model": "Focus",
            "trim": "Zetec",
            "year": 2014,
            "mileage": 29000,
            "vrm": "AB09 ABC",
            "labour_quantity": 1,
            "labour_unit": 10.00,
            "new_line_items": [
                {
                    "description": "Oil Change",
                    "quantity": 1,
                    "unit_price": 25.00,
                },
                {
                    "description": "Air Filter Change",
                    "quantity": 1,
                    "unit_price": 15.00,
                },
            ],
            "comments": "Test invoice with working serializer.",
        }
        serializer = InvoiceSerializer(data=data, many=False)
        self.assertTrue(serializer.is_valid())

    def get_customer_in_database(self):
        customer = Customer.objects.get(
            first_name="Cameron",
            email="testCam@example.com"
        )
        response = get_customer(customer_data=customer.customer_id)
        self.assertEqual(response, customer.id)

    def get_customer_not_in_database(self):
        data = {
            "first_name": "James",
            "last_name": "Bell",
            "phone_number": "071113456789",
            "email": "testJames@example.com",
            "address_line_1": "27 Test\'s Lane",
            "address_line_2": "",
            "town_city": "Crewe",
            "county": "Cheshire",
            "postcode": "AA4 7AA"
        }
        self.assertFalse(Customer.objects.filter(
            first_name="James",
            last_name="Bell",
            email="testJames@example.com",
            phone_number="071113456789"
        ).exists())
        get_customer(customer_data=data)
        self.assertTrue(Customer.objects.filter(
            first_name="James",
            last_name="Bell",
            email="testJames@example.com",
            phone_number="071113456789"
        ).exists())

    def customer_str(self):
        customer = Customer.objects.get(
            first_name="Cameron",
            last_name="Fitzgerald",
            phone_number="07123456781",
            email="testCam@example.com"
        )
        self.assertEqual(str(customer), 'Cameron Fitzgerald')

    def invoice_item_str(self):
        invoice = Invoice.objects.get(
            make="Mercedes",
            model="Sprinter",
            trim="2.1 CDI",
            year=2013,
            mileage=72000,
            vrm="DK19 CLX"
        )
        InvoiceItem.objects.create(
            invoice=invoice,
            description="Test description no.1",
            quantity=2,
            unit_price=10.00,
            line_price=20.00
        )
        invoice_item = InvoiceItem.objects.get(
            invoice=invoice,
            description="Test description no.1",
            quantity=2,
            unit_price=10.00,
            line_price=20.00
        )
        self.assertEqual(
            str(invoice_item),
            "Test description no.1 - £20.00"
        )

    def invoice_str(self):
        invoice = Invoice.objects.get(
            make="Mercedes",
            model="Sprinter",
            trim="2.1 CDI",
            year=2013,
            mileage=72000,
            vrm="DK19 CLX"
        )
        self.assertEqual(str(invoice), f"{invoice.invoice_id} - DK19 CLX")

    def invoice_get_total(self):
        invoice = Invoice.objects.get(
            make="Mercedes",
            model="Sprinter",
            trim="2.1 CDI",
            year=2013,
            mileage=72000,
            vrm="DK19 CLX"
        )
        self.assertEqual(invoice.get_total(), 45.00)

    def test_in_order(self):
        self.customer_serializer_working()
        self.invoice_item_serializer_working()
        self.invoice_serializer_working()
        self.get_customer_in_database()
        self.get_customer_not_in_database()
        self.customer_str()
        self.invoice_item_str()
        self.invoice_str()
        self.invoice_get_total()

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestBusinessAdminInvoice(APITestCase):

    def setUp(self):
        user = get_user_model()
        user.objects.create(
            first_name= 'Harold',
            last_name= 'Finch',
            username= 'admin',
            password=make_password('TestP455word!'),
            is_staff=True
        ).save()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def sending_invoice_by_email_working(self):
        # Get access token
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']

        # Check customer isn't already in the DB
        self.assertFalse(Customer.objects.filter(
            first_name="Elizbath",
            last_name="Windsor",
            email="test@example.com",
            phone_number="07123456789"
        ).exists())

        # Send post to create invoice
        response = self.client.post(
            '/api/admin/invoice/',
            {
                "customer": {
                    "first_name": "Elizbath",
                    "last_name": "Windsor",
                    "phone_number": "07123456789",
                    "email": "test@example.com",
                    "address_line_1": "1 The Mall",
                    "address_line_2": "",
                    "town_city": "Westminter",
                    "county": "London",
                    "postcode": "SW1A 1AA"
                },
                "make": "Land Rover",
                "model": "Defender",
                "trim": "110",
                "year": 2021,
                "mileage": 250,
                "vrm": "B16 LIZ",
                "labour_quantity": 10,
                "labour_unit": 15,
                "new_line_items": [
                    {
                        "description": "Oil Change",
                        "quantity": 1,
                        "unit_price": 25.00,
                    },
                    {
                        "description": "Air Filter Change",
                        "quantity": 1,
                        "unit_price": 15.00,
                    },
                ],
                "comments": "Testing sending of pdf email",
            },
            format='json',
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )

        # Check Page Response
        self.assertEqual(response.status_code, 200)

        # Check that the customer is added to the DB
        self.assertTrue(Customer.objects.filter(
            first_name="Elizbath",
            last_name="Windsor",
            email="test@example.com",
            phone_number="07123456789"
        ).exists())

        # Check Invoice
        invoice = Invoice.objects.get(
            make="Land Rover",
            model="Defender",
            trim="110",
            year=2021,
            mileage=250,
            vrm="B16 LIZ",
        )
        self.assertEqual(invoice.customer.first_name, "Elizbath")
        self.assertEqual(invoice.customer.last_name, "Windsor")
        self.assertEqual(invoice.customer.email, "test@example.com")
        self.assertEqual(invoice.customer.phone_number, "07123456789")
        self.assertEqual(invoice.make, "Land Rover")
        self.assertEqual(invoice.model, "Defender")
        self.assertEqual(invoice.trim, "110")
        self.assertEqual(invoice.year, 2021)
        self.assertEqual(invoice.mileage, 250)
        self.assertEqual(invoice.vrm, "B16 LIZ")
        self.assertEqual(invoice.labour_quantity, 10.00)
        self.assertEqual(invoice.labour_unit, 15.00)
        self.assertEqual(invoice.labour_total, 150.00)
        self.assertEqual(invoice.invoice_total, 190.00)
        self.assertEqual(invoice.comments, "Testing sending of pdf email")

        # Check both line items exists in DB
        self.assertTrue(InvoiceItem.objects.filter(
            description="Oil Change",
            quantity=1,
            unit_price=25.00,
            line_price=25.00
        ).exists())

        self.assertTrue(InvoiceItem.objects.filter(
            description="Air Filter Change",
            quantity=1,
            unit_price=15.00,
            line_price=15.00
        ).exists())

    def sending_invoice_by_email_serializer_invalid(self):
        # Get access token
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']

        # Send post to create invoice
        response = self.client.post(
            '/api/admin/invoice/',
            {
                "customer": {
                    "first_name": "Elizbath",
                    "last_name": "Windsor",
                    "phone_number": "07123456789",
                    "email": "test@example.com",
                    "address_line_1": "1 The Mall",
                    "address_line_2": "",
                    "town_city": "Westminter",
                    "county": "London",
                    "postcode": "SW1A 1AA"
                },
                "make": "Land Rover",
                "model": "Defender",
                "trim": "110",
                "year": 2021,
                "mileage": 250,
                "vrm": "",
                "labour_quantity": 10,
                "labour_unit": 15,
                "new_line_items": [
                    {
                        "description": "Oil Change",
                        "quantity": 1,
                        "unit_price": 25.00,
                    },
                    {
                        "description": "Air Filter Change",
                        "quantity": 1,
                        "unit_price": 15.00,
                    },
                ],
                "comments": "Testing sending of pdf email",
            },
            format='json',
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {
                "vrm": ["This field may not be blank."]
            }
        )

    def test_in_order(self):
        self.sending_invoice_by_email_working()
        self.sending_invoice_by_email_serializer_invalid()

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

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestBusinessAdminGallery(APITestCase):

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

    def update_gallery_with_images(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        gallery = GalleryItem.objects.get(
            make="Nissan",
            model="Skyline",
            trim="GTR V-spec",
            year=2001
        )
        response = self.client.patch(
            f'/api/admin/gallery/{gallery.slug}/',
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(GalleryImage.objects.filter(
            item_id=gallery.id
        ).count(), 4)

    def update_gallery_without_images(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        gallery = GalleryItem.objects.get(
            make="Nissan",
            model="Skyline",
            trim="GTR V-spec",
            year=2001
        )
        response = self.client.patch(
            f'/api/admin/gallery/{gallery.slug}/',
            {
                "make": "Nissan",
                "model": "Skyline",
                "trim": "GTR V-spec",
                "year": 2000,
                "description": "A proper description",
                "published": True,
                "uploaded_images": []
            },
            format="multipart",
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(GalleryImage.objects.filter(
            item_id=gallery.id
        ).count(), 4)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['year'], 2000)
        self.assertEqual(json_response['description'], 'A proper description')

    def delete_gallery_image(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        image = GalleryImage.objects.filter(
            item__slug="nissan-skyline-gtr-v-spec-2000"
        ).first()
        response = self.client.delete(
            f'/api/admin/gallery/image/{image.id}/',
            **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(GalleryImage.objects.filter(
            item_id=image.item.id
        ).count(), 3)

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
        self.create_gallery_no_images()
        self.create_gallery_with_images()
        self.get_gallery()
        self.update_gallery_with_images()
        self.update_gallery_without_images()
        self.delete_gallery_image()
        self.delete_gallery()
