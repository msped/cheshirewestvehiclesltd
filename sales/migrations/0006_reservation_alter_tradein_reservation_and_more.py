# Generated by Django 4.1.4 on 2023-03-18 22:12

import datetime
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0005_alter_tradein_year_alter_vehicle_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(blank=True, editable=False, max_length=10, unique=True)),
                ('name', models.CharField(max_length=75)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('reservation_date', models.DateField(default=datetime.date.today)),
                ('paymentIntent_id', models.CharField(blank=True, max_length=150, null=True)),
                ('paid', models.BooleanField(default=False)),
                ('vehicle', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.vehicle')),
            ],
        ),
        migrations.AlterField(
            model_name='tradein',
            name='reservation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.reservation'),
        ),
        migrations.DeleteModel(
            name='Reservations',
        ),
    ]
