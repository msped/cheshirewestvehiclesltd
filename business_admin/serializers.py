from rest_framework import serializers

from .models import Invoice, InvoiceItem, Customer
from .utils import get_customer

class CustomerSerializer(serializers.ModelSerializer):
    customer_id = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            'id',
            'customer_id',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'address_line_1',
            'address_line_2',
            'town_city',
            'county',
            'postcode',
        ]

class InvoiceItemSerializer(serializers.ModelSerializer):
    invoice = serializers.ReadOnlyField()
    line_price = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False
    )

    class Meta:
        model = InvoiceItem
        fields = [
            'invoice',
            'description',
            'quantity',
            'unit_price',
            'line_price'
        ]

class InvoiceSerializer(serializers.ModelSerializer):
    invoice_id = serializers.ReadOnlyField()
    created_date=serializers.ReadOnlyField()
    customer = CustomerSerializer(many=False)
    line_items = serializers.SerializerMethodField(read_only=True)
    new_line_items = serializers.ListField(
        child=InvoiceItemSerializer(),
        write_only=True,
        required=False
    )
    labour_total = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False
    )
    invoice_total = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False
    )

    class Meta:
        model = Invoice
        fields = [
            'invoice_id',
            'created_date',
            'customer',
            'make',
            'model',
            'trim',
            'year',
            'mileage',
            'vrm',
            'labour_quantity',
            'labour_unit',
            'labour_total',
            'line_items',
            'invoice_total',
            'comments',
            'new_line_items'
        ]

    def get_line_items(self, obj):
        items = InvoiceItem.objects.filter(invoice_id=obj.id)
        serializer = InvoiceItemSerializer(items, many=True)
        return serializer.data

    def create(self, validated_data):
        customer = get_customer(validated_data.pop('customer'))
        if 'new_line_items' in validated_data:
            invoice_items = validated_data.pop('new_line_items')
            invoice = Invoice.objects.create(customer_id=customer, **validated_data)
            for item in invoice_items:
                InvoiceItem.objects.create(invoice=invoice, **item)
        else:
            invoice = Invoice.objects.create(customer_id=customer, **validated_data)
        invoice.invoice_total = invoice.get_total()
        invoice.save()
        return invoice
