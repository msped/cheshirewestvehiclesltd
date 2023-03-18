import datetime
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.utils.text import slugify

from auditlog.registry import auditlog


class Vehicle(models.Model):
    """Vehicle Model"""
    class Reserve(models.TextChoices):
        """Options for Fuel"""
        FOR_SALE = "1", "For Sale"
        RESERVED = "2", "Reserved"
        SOLD = "3", "Sold"

    class Fuel(models.TextChoices):
        """Options for Fuel"""
        PETROL = "1", "Petrol"
        DIESEL = "2", "Diesel"
        HYBRID = "3", "Hybrid"
        ELECTRIC = "4", "Electric"

    class CarState(models.TextChoices):
        """State of sale"""
        TRADE_IN = "1", "Trade-in"
        FRONTLINE = "2", "Frontline"

    class BodyType(models.TextChoices):
        """Body Type of vehicle"""
        COUPE = "1", "Coupe"
        HATCHBACK = "2", "Hatchback"
        SALOON = "3", "Saloon"
        ESTATE = "4", " Estate"
        VAN = "5", "Van"
        CONVERTIBLE = "6", "Convertible"

    slug = models.SlugField(unique=True, null=True, blank=True)
    make = models.CharField(max_length=15)
    model = models.CharField(max_length=15)
    trim = models.CharField(max_length=30)
    year = models.IntegerField(
        choices=[(x, str(x))
                 for x in range(1980, datetime.date.today().year+1)],
        default=datetime.date.today().year
    )
    fuel = models.CharField(max_length=8, choices=Fuel.choices, default="1")
    body_type = models.CharField(
        max_length=8, choices=BodyType.choices, default="1")
    car_state = models.CharField(
        max_length=8, choices=CarState.choices, default="1")
    reserved = models.CharField(
        max_length=8, choices=Reserve.choices, default="1")
    mileage = models.IntegerField()
    engine_size = models.IntegerField()
    mot_expiry = models.DateField()
    extras = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]

    def is_for_sale(self):
        if self.reserved == "1":
            return True
        return False

    def __str__(self):
        return f"{self.id} {self.make} {self.model} {self.trim} - £{self.price}"

    def save(self, *args, **kwargs):
        self.slug = slugify(
            f'{self.make} {self.model} {self.trim} {self.year}')
        super(Vehicle, self).save(*args, **kwargs)


class VehicleImages(models.Model):
    """Images relating to a vehicle"""
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="vehicle_images")

    def __str__(self):
        return f"{self.vehicle.id} - {self.id}"


class Reservation(models.Model):
    order_id = models.CharField(
        max_length=10,
        blank=True,
        unique=True,
        editable=False
    )
    name = models.CharField(max_length=75)
    email = models.EmailField()
    phone_number = PhoneNumberField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)
    reservation_date = models.DateField(default=datetime.date.today)
    paymentIntent_id = models.CharField(max_length=150, blank=True, null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} reserved {self.vehicle}'

    def save(self, *args, **kwargs):
        if not self.order_id:
            today = datetime.date.today()
            today_string = today.strftime('%y%m%d')
            next_reservation_number = '001'
            last_reservation = Reservation.objects.filter(
                order_id__startswith=today_string
            ).order_by('order_id').last()
            if last_reservation:
                last_reservation_number = int(last_reservation.order_id[7:])
                next_reservation_number = f"{last_reservation_number + 1:03d}"
            self.order_id = f'{today_string}3{next_reservation_number}'
        super(Reservation, self).save(*args, **kwargs)


class TradeIn(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    make = models.CharField(max_length=15)
    model = models.CharField(max_length=15)
    trim = models.CharField(max_length=30)
    year = models.IntegerField(
        choices=[(x, str(x))
                 for x in range(1980, datetime.date.today().year+1)],
        default=datetime.date.today().year
    )
    mileage = models.IntegerField()
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Trade In Vehicle for {self.reservation.id}'


class ReservationAmount(models.Model):
    amount = models.IntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        activity = "Inactive"
        formatted_currency = '{:.2f}'.format(self.amount / 100)
        if self.active:
            activity = "Active"
        return f'£{formatted_currency} - {activity}'


auditlog.register(Vehicle)
auditlog.register(VehicleImages)
auditlog.register(Reservation)
auditlog.register(TradeIn)
auditlog.register(ReservationAmount)
