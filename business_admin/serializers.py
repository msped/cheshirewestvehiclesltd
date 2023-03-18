from rest_framework import serializers

from .models import Invoice, InvoiceItem, Customer
from .utils import get_customer, create_invoice_items

# pylint: disable=W0223


class ResendInvoiceSerializer(serializers.Serializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
        required=True,
        allow_empty=False
    )


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
    line_price = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False
    )

    class Meta:
        model = InvoiceItem
        fields = [
            'id',
            'invoice',
            'description',
            'quantity',
            'unit_price',
            'line_price'
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    invoice_id = serializers.ReadOnlyField()
    created_date = serializers.DateTimeField(
        read_only=True, format="%Y-%m-%d %H:%M:%S")
    customer = CustomerSerializer(many=False)
    line_items = InvoiceItemSerializer(many=True, read_only=True)
    new_line_items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    labour_total = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False
    )
    vat = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False
    )
    invoice_total = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False
    )
    audit_log = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id',
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
            'vat',
            'invoice_total',
            'comments',
            'new_line_items',
            'audit_log'
        ]

    def get_audit_log(self, obj):
        return obj.audit_log.latest().changes_dict

    def create(self, validated_data):
        customer = get_customer(validated_data.pop('customer'))
        new_items = validated_data.pop('new_line_items', None)
        invoice = Invoice.objects.create(
            customer_id=customer, **validated_data)

        if new_items:
            create_invoice_items(invoice.id, new_items)
        invoice.invoice_total = invoice.get_total()
        invoice.save()
        return invoice

    def update(self, instance, validated_data):
        if 'new_line_items' in validated_data:
            create_invoice_items(
                instance.id, validated_data.pop('new_line_items'))
        super().update(instance, validated_data)
        return instance


class CustomerInvoicesSerializer(serializers.ModelSerializer):
    invoices = serializers.SerializerMethodField()

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
            'invoices'
        ]

    def get_invoices(self, obj):
        data = Invoice.objects.filter(customer__customer_id=obj.customer_id)
        serializer = InvoiceSerializer(data, many=True)
        return serializer.data
