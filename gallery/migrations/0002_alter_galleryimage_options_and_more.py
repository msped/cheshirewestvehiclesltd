# Generated by Django 4.1.4 on 2023-01-06 22:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='galleryimage',
            options={'ordering': ['id']},
        ),
        migrations.RemoveField(
            model_name='galleryimage',
            name='order_of_images',
        ),
    ]
