import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import override_settings
from rest_framework.test import APITestCase

from .models import Customer, InvoiceItem, Invoice
from .serializers import (
    InvoiceItemSerializer,
    InvoiceSerializer,
    CustomerSerializer,
    ResendInvoiceSerializer
)
from .utils import get_customer

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestInvoiceModelsAndSerializers(APITestCase):

    def setUp(self):
        user = get_user_model()
        user.objects.create(
            first_name='Harold',
            last_name='Finch',
            username='admin',
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
            vat=4.00,
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
        invoice = Invoice.objects.get(
            make="Mercedes",
            model="Sprinter",
            trim="2.1 CDI",
            year=2013,
            mileage=72000,
            vrm="DK19 CLX",
        )
        data = {
            "invoice": invoice.id,
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

    def resend_invoice_serializer_working(self):
        data = {
            "emails": ['matt@mspe.me', 'test@example.com']
        }
        serializer = ResendInvoiceSerializer(data=data, many=False)
        self.assertTrue(serializer.is_valid())

    def resend_invoice_serializer_not_working(self):
        data = {
            "emails": []
        }
        serializer = ResendInvoiceSerializer(data=data, many=False)
        self.assertFalse(serializer.is_valid())

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
        self.assertEqual(invoice.get_total(), 54.00)

    def test_in_order(self):
        self.customer_serializer_working()
        self.invoice_item_serializer_working()
        self.invoice_serializer_working()
        self.resend_invoice_serializer_working()
        self.resend_invoice_serializer_not_working()
        self.get_customer_in_database()
        self.get_customer_not_in_database()
        self.customer_str()
        self.invoice_item_str()
        self.invoice_str()
        self.invoice_get_total()
