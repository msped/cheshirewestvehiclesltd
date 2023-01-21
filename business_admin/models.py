import datetime
from django.utils import timezone
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

class Customer(models.Model):
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone_number=PhoneNumberField()
    email=models.EmailField(blank=True, null=True)
    address_line_1=models.CharField(max_length=50)
    address_line_2=models.CharField(max_length=50)
    town_city=models.CharField(max_length=50)
    county=models.CharField(max_length=35)
    postcode=models.CharField(max_length=10)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class InvoiceLabour(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
    quantity=models.IntegerField()
    unit=models.DecimalField(max_digits=6, decimal_places=2)
    total=models.DecimalField(max_digits=6, decimal_places=2)

    def get_total(self):
        return round(self.quantity * self.unit, 2)

    def __str__(self):
        return f'{self.quantity} at £{self.unit} per hour'

    def save(self, *args, **kwargs):
        self.total = self.get_total()
        super(InvoiceLabour, self).save(*args, **kwargs)

class Invoice(models.Model):
    invoice_id = models.CharField(
        max_length=9,
        blank=True,
        unique=True,
        editable=False
    )
    created_date=models.DateTimeField(auto_now_add=timezone.now())
    customer=models.ForeignKey(Customer, on_delete=models.PROTECT)
    make=models.CharField(max_length=75)
    model=models.CharField(max_length=100)
    trim=models.CharField(max_length=150)
    year=models.IntegerField()
    mileage=models.IntegerField()
    vrm=models.CharField(max_length=10)
    total=models.DecimalField(max_digits=6, decimal_places=2)
    comments=models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.invoice_id} - {self.vrm}'

    def get_total(self):
        total = 0
        items = InvoiceItem.objects.filter(invoice_id=self.id)
        if items:
            for item in items:
                total += item.line_price
        labour = InvoiceLabour.objects.get(invoice_id=self.id)
        if labour:
            total += labour.total
        return round(total, 2)

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            today = datetime.date.today()
            today_string = today.strftime('%y%m%d')
            next_invoice_number = '01'
            last_invoice = Invoice.objects.filter(
                invoice_id__startswith=today_string
            ).order_by('invoice_id').last()
            if last_invoice:
                last_invoice_number = int(last_invoice.invoice_id[6:])
                next_invoice_number = '{0:03d}'.format(last_invoice_number + 1)
            self.invoice_id = today_string + next_invoice_number
        self.total = self.get_total()
        super(Invoice, self).save(*args, **kwargs)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
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
