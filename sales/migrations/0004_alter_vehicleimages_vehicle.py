# Generated by Django 4.1.4 on 2022-12-31 17:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_remove_vehicleimages_order_of_images_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleimages',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='sales.vehicle'),
        ),
    ]
