# Generated by Django 4.1.4 on 2022-12-31 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_reservations_paid_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicleimages',
            name='order_of_images',
        ),
        migrations.AddField(
            model_name='vehicle',
            name='published',
            field=models.BooleanField(default=False),
        ),
    ]