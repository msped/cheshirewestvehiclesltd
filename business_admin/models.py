import datetime
from django.utils import timezone
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

class Customer(models.Model):
    customer_id = models.CharField(
        max_length=9,
        blank=True,
        unique=True,
        editable=False
    )
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone_number=PhoneNumberField()
    email=models.EmailField(blank=True, null=True)
    address_line_1=models.CharField(max_length=50)
    address_line_2=models.CharField(max_length=50, blank=True, null=True)
    town_city=models.CharField(max_length=50)
    county=models.CharField(max_length=35)
    postcode=models.CharField(max_length=10)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        if not self.customer_id:
            today = datetime.date.today()
            today_string = today.strftime('%y%m%d')
            next_customer_number = '001'
            last_customer = Customer.objects.filter(
                customer_id__startswith=today_string
            ).order_by('customer_id').last()
            if last_customer:
                last_customer_number = int(last_customer.customer_id[6:])
                next_customer_number = '{0:03d}'.format(last_customer_number + 1)
            self.customer_id = today_string + next_customer_number
        super(Customer, self).save(*args, **kwargs)

class Invoice(models.Model):
    invoice_id = models.CharField(
        max_length=9,
        blank=True,
        unique=True,
        editable=False
    )
    created_date=models.DateTimeField(auto_now_add=timezone.now())
    customer=models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="customer"
    )
    make=models.CharField(max_length=75)
    model=models.CharField(max_length=100)
    trim=models.CharField(max_length=150)
    year=models.IntegerField()
    mileage=models.IntegerField()
    vrm=models.CharField(max_length=10)
    labour_quantity=models.IntegerField(default=0)
    labour_unit=models.DecimalField(max_digits=6, decimal_places=2, default=0)
    labour_total=models.DecimalField(max_digits=6, decimal_places=2, default=0)
    invoice_total=models.DecimalField(max_digits=6, decimal_places=2, default=0)
    comments=models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.invoice_id} - {self.vrm}'

    def get_labour_total(self):
        total = self.labour_quantity * self.labour_unit
        return round(total, 2)

    def get_total(self):
        total = 0
        items = InvoiceItem.objects.filter(invoice_id=self.id)
        if items:
            for item in items:
                total += item.line_price
        total += self.get_labour_total()
        return round(total, 2)

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            today = datetime.date.today()
            today_string = today.strftime('%y%m%d')
            next_invoice_number = '001'
            last_invoice = Invoice.objects.filter(
                invoice_id__startswith=today_string
            ).order_by('invoice_id').last()
            if last_invoice:
                last_invoice_number = int(last_invoice.invoice_id[6:])
                next_invoice_number = '{0:03d}'.format(last_invoice_number + 1)
            self.invoice_id = today_string + next_invoice_number
        self.labour_total = self.get_labour_total()
        super(Invoice, self).save(*args, **kwargs)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
    description=models.TextField()
    quantity=models.IntegerField()
    unit_price=models.DecimalField(max_digits=6, decimal_places=2)
    line_price=models.DecimalField(max_digits=6, decimal_places=2)

    def get_total(self):
        return round(self.quantity * self.unit_price, 2)

    def save(self, *args, **kwargs):
        self.line_price = self.get_total()
        super(InvoiceItem, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.description} - £{self.line_price}'
