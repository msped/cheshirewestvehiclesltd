import json
import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import override_settings
from rest_framework.test import APITestCase

from .models import Customer, InvoiceItem, Invoice

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestBusinessAdminInvoice(APITestCase):

    def setUp(self):
        user = get_user_model()
        user.objects.create(
            first_name='Harold',
            last_name='Finch',
            username='admin',
            password=make_password('TestP455word!'),
            is_staff=True
        ).save()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def get_access_token(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        return access_request.data['access']

    def sending_invoice_by_email_working(self):
        # Check customer isn't already in the DB
        self.assertFalse(Customer.objects.filter(
            first_name="Elizabeth",
            last_name="Windsor",
            email="test@example.com",
            phone_number="07123456789"
        ).exists())

        # Send post to create invoice
        response = self.client.post(
            '/api/admin/invoice/',
            {
                "customer": {
                    "first_name": "Elizabeth",
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
            format="json",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )

        # Check Page Response
        self.assertEqual(response.status_code, 200)

        # Check that the customer is added to the DB
        self.assertTrue(Customer.objects.filter(
            first_name="Elizabeth",
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
        self.assertEqual(invoice.customer.first_name, "Elizabeth")
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
        self.assertEqual(invoice.invoice_total, 228.00)
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

    def sending_invoice_by_email_working_no_line_items(self):
        # Check customer isn't already in the DB
        self.assertFalse(Customer.objects.filter(
            first_name="John",
            last_name="Reese",
            email="JReese@samaritan.com",
            phone_number="07976449741"
        ).exists())

        # Send post to create invoice
        response = self.client.post(
            '/api/admin/invoice/',
            {
                "customer": {
                    "first_name": "John",
                    "last_name": "Reese",
                    "phone_number": "07976449741",
                    "email": "JReese@samaritan.com",
                    "address_line_1": "1 The Library",
                    "address_line_2": "",
                    "town_city": "York",
                    "county": "North Yorkshire",
                    "postcode": "YO1 OSB"
                },
                "make": "Ford",
                "model": "Mustang",
                "trim": "GT",
                "year": 2016,
                "mileage": 32000,
                "vrm": "MK16 YGB",
                "labour_quantity": 1,
                "labour_unit": 15,
                "comments": "Testing sending of pdf email without line items",
            },
            format='json',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )

        # Check Page Response
        self.assertEqual(response.status_code, 200)

        # Check that the customer is added to the DB
        self.assertTrue(Customer.objects.filter(
            first_name="John",
            last_name="Reese",
            email="JReese@samaritan.com",
            phone_number="07976449741"
        ).exists())

        # Check Invoice
        invoice = Invoice.objects.get(
            make="Ford",
            model="Mustang",
            trim="GT",
            year=2016,
            mileage=32000,
            vrm="MK16 YGB",
        )
        self.assertEqual(invoice.customer.first_name, "John")
        self.assertEqual(invoice.customer.last_name, "Reese")
        self.assertEqual(invoice.customer.email, "JReese@samaritan.com")
        self.assertEqual(invoice.customer.phone_number, "07976449741")
        self.assertEqual(invoice.make, "Ford")
        self.assertEqual(invoice.model, "Mustang")
        self.assertEqual(invoice.trim, "GT")
        self.assertEqual(invoice.year, 2016)
        self.assertEqual(invoice.mileage, 32000)
        self.assertEqual(invoice.vrm, "MK16 YGB")
        self.assertEqual(invoice.labour_quantity, 1)
        self.assertEqual(invoice.labour_unit, 15.00)
        self.assertEqual(invoice.labour_total, 15.00)
        self.assertEqual(invoice.invoice_total, 18.00)
        self.assertEqual(invoice.comments,
                         "Testing sending of pdf email without line items")

        # Check no line items exist in DB
        self.assertFalse(InvoiceItem.objects.filter(
            invoice_id=invoice.id
        ).exists())

    def search_invoice_using_invoice_id(self):
        invoice = Invoice.objects.get(
            customer__first_name='Elizabeth',
            customer__last_name='Windsor',
            customer__email='test@example.com'
        )
        response = self.client.get(
            '/api/admin/invoice',
            {
                'search': invoice.invoice_id,
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)

    def resending_invoice_standard_recepient(self):
        invoice = Invoice.objects.get(
            customer__first_name='Elizabeth',
            customer__last_name='Windsor',
            customer__email='test@example.com'
        )
        response = self.client.post(
            f'/api/admin/invoice/{invoice.invoice_id}/send/',
            {
                'emails': [invoice.customer.email]
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)

    def resending_invoice_extra_emails(self):
        invoice = Invoice.objects.get(
            customer__first_name='Elizabeth',
            customer__last_name='Windsor',
            customer__email='test@example.com'
        )
        response = self.client.post(
            f'/api/admin/invoice/{invoice.invoice_id}/send/',
            {
                'emails': ['matt@mspe.me',]
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)

    def resending_invoice_no_emails(self):
        invoice = Invoice.objects.get(
            customer__first_name='Elizabeth',
            customer__last_name='Windsor',
            customer__email='test@example.com'
        )
        response = self.client.post(
            f'/api/admin/invoice/{invoice.invoice_id}/send/',
            {
                'emails': []
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 400)

    def search_invoice_using_created_date(self):
        invoice = Invoice.objects.get(
            customer__first_name='Elizabeth',
            customer__last_name='Windsor',
            customer__email='test@example.com'
        )
        response = self.client.get(
            '/api/admin/invoice',
            {
                'search': f'{invoice.created_date:%Y-%m-%d %H:%M:%S}',
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)

    def search_invoice_using_vrm(self):
        invoice = Invoice.objects.get(
            customer__first_name='Elizabeth',
            customer__last_name='Windsor',
            customer__email='test@example.com'
        )

        response = self.client.get(
            '/api/admin/invoice',
            {
                'search': invoice.vrm,
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)

    def search_invoice_doesnt_exist(self):
        response = self.client.get(
            '/api/admin/invoice',
            {
                'search': "9999999999",
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {
                "count": 0,
                "next": None,
                "previous": None,
                "results": []
            }
        )

    def search_customer_using_customer_id(self):
        customer = Customer.objects.get(
            first_name='Elizabeth',
            last_name='Windsor',
            email='test@example.com'
        )
        response = self.client.get(
            '/api/admin/customer',
            {
                'search': customer.customer_id,
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            [{
                "id": 1,
                "customer_id": customer.customer_id,
                "first_name": "Elizabeth",
                "last_name": "Windsor",
                "phone_number": "07123 456789",
                "email": "test@example.com",
                "address_line_1": "1 The Mall",
                "address_line_2": "",
                "town_city": "Westminter",
                "county": "London",
                "postcode": "SW1A 1AA"
            }]
        )

    def search_customer_using_name(self):
        customer = Customer.objects.get(
            first_name='Elizabeth',
            last_name='Windsor',
            email='test@example.com'
        )
        response = self.client.get(
            '/api/admin/customer',
            {
                'search': f'{customer.first_name} {customer.last_name}',
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            [{
                "id": 1,
                "customer_id": customer.customer_id,
                "first_name": "Elizabeth",
                "last_name": "Windsor",
                "phone_number": "07123 456789",
                "email": "test@example.com",
                "address_line_1": "1 The Mall",
                "address_line_2": "",
                "town_city": "Westminter",
                "county": "London",
                "postcode": "SW1A 1AA"
            }]
        )

    def search_customer_using_email(self):
        customer = Customer.objects.get(
            first_name='Elizabeth',
            last_name='Windsor',
            email='test@example.com'
        )
        response = self.client.get(
            '/api/admin/customer',
            {
                'search': customer.email,
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            [{
                "id": 1,
                "customer_id": customer.customer_id,
                "first_name": "Elizabeth",
                "last_name": "Windsor",
                "phone_number": "07123 456789",
                "email": "test@example.com",
                "address_line_1": "1 The Mall",
                "address_line_2": "",
                "town_city": "Westminter",
                "county": "London",
                "postcode": "SW1A 1AA"
            }]
        )

    def search_customer_using_phone_number(self):
        customer = Customer.objects.get(
            first_name='Elizabeth',
            last_name='Windsor',
            email='test@example.com'
        )
        response = self.client.get(
            '/api/admin/customer',
            {
                'search': str(customer.phone_number),
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            [{
                "id": 1,
                "customer_id": customer.customer_id,
                "first_name": "Elizabeth",
                "last_name": "Windsor",
                "phone_number": "07123 456789",
                "email": "test@example.com",
                "address_line_1": "1 The Mall",
                "address_line_2": "",
                "town_city": "Westminter",
                "county": "London",
                "postcode": "SW1A 1AA"
            }]
        )

    def search_customer_doesnt_exist(self):
        response = self.client.get(
            '/api/admin/customer',
            {
                'search': '230427669',
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            []
        )

    def sending_invoice_by_email_serializer_invalid(self):
        # Get access token

        # Send post to create invoice
        response = self.client.post(
            '/api/admin/invoice/',
            {
                "customer": {
                    "first_name": "Elizabeth",
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
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {
                "vrm": ["This field may not be blank."]
            }
        )

    def get_customer(self):
        customer = Customer.objects.get(
            first_name='Elizabeth',
            last_name='Windsor',
            email='test@example.com'
        )
        response = self.client.get(
            f'/api/admin/customer/{customer.customer_id}/',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)

    def update_customer(self):
        customer = Customer.objects.get(
            first_name='Elizabeth',
            last_name='Windsor',
            email='test@example.com'
        )
        response = self.client.patch(
            f'/api/admin/customer/{customer.customer_id}/',
            {
                'email': 'test10@example.com'
            },
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {
                "id": 1,
                "customer_id": customer.customer_id,
                "first_name": "Elizabeth",
                "last_name": "Windsor",
                "phone_number": "07123 456789",
                "email": "test10@example.com",
                "address_line_1": "1 The Mall",
                "address_line_2": "",
                "town_city": "Westminter",
                "county": "London",
                "postcode": "SW1A 1AA"
            }
        )

    def destroy_customer_with_invoice_still_active(self):
        customer = Customer.objects.get(
            first_name='Elizabeth',
            last_name='Windsor',
            email='test@example.com'
        )
        response = self.client.delete(
            f'/api/admin/customer/{customer.customer_id}/',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {
                'error': 'Customer object cannot be deleted with Invoice objects still active.'
            }
        )

    def destroy_customer(self):
        customer = Customer.objects.get(
            first_name='Elizabeth',
            last_name='Windsor',
            email='test10@example.com'
        )
        response = self.client.delete(
            f'/api/admin/customer/{customer.customer_id}/',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 204)

    def get_customer_doesnt_exist(self):
        response = self.client.get(
            '/api/admin/customer/365735300/',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 404)

    def get_invoice_not_found(self):
        response = self.client.get(
            '/api/admin/invoice/36573523/',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 404)

    def get_invoice_working(self):
        invoice = Invoice.objects.get(customer__first_name="Elizabeth")
        response = self.client.get(
            f'/api/admin/invoice/{invoice.invoice_id}/',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)

    def update_invoice_not_found(self):
        response = self.client.get(
            '/api/admin/invoice/675487644/',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 404)

    def update_invoice_working(self):
        invoice = Invoice.objects.get(customer__first_name="Elizabeth")

        # Check only two original line items
        self.assertEqual(
            InvoiceItem.objects.filter(
                invoice_id=invoice.id
            ).count(),
            2
        )

        response = self.client.patch(
            f'/api/admin/invoice/{invoice.invoice_id}/',
            {
                "new_line_items": [
                    {
                        "description": "Front Splitter",
                        "quantity": 1,
                        "unit_price": 500.00
                    },
                ]
            },
            format="json",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            InvoiceItem.objects.filter(
                invoice_id=invoice.id
            ).count(),
            3
        )

    def destroy_invoice_not_found(self):
        response = self.client.get(
            '/api/admin/invoice/8789456345/',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 404)

    def destroy_invoice_working(self):
        invoice = Invoice.objects.get(customer__first_name="Elizabeth")
        response = self.client.delete(
            f'/api/admin/invoice/{invoice.invoice_id}/',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 204)

    def test_in_order(self):
        self.sending_invoice_by_email_working()
        self.sending_invoice_by_email_working_no_line_items()
        self.sending_invoice_by_email_serializer_invalid()
        self.search_invoice_using_invoice_id()
        self.search_invoice_using_created_date()
        self.search_invoice_using_vrm()
        self.search_invoice_doesnt_exist()
        self.search_customer_using_customer_id()
        self.search_customer_using_name()
        self.search_customer_using_email()
        self.search_customer_using_phone_number()
        self.search_customer_doesnt_exist()
        self.get_customer()
        self.destroy_customer_with_invoice_still_active()
        self.get_customer_doesnt_exist()
        self.get_invoice_not_found()
        self.get_invoice_working()
        self.resending_invoice_standard_recepient()
        self.resending_invoice_extra_emails()
        self.resending_invoice_no_emails()
        self.update_invoice_not_found()
        self.update_invoice_working()
        self.destroy_invoice_not_found()
        self.destroy_invoice_working()
        self.update_customer()
        self.destroy_customer()
