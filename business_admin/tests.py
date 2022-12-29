from rest_framework.test import APITestCase
from rest_framework import status

# Create your tests here.

class TestBusinessAdmin(APITestCase):

    def test_sending_invoice_by_email(self):
        data = {
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
        }
        response = self.client.post(
            '/api/admin/invoice/',
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
