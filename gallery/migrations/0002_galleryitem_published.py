# Generated by Django 4.1.4 on 2022-12-18 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='galleryitem',
            name='published',
            field=models.BooleanField(default=False),
        ),
    ]
