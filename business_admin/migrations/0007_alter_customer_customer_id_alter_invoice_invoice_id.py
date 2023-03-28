# Generated by Django 4.1.4 on 2023-03-11 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business_admin', '0006_alter_invoice_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='customer_id',
            field=models.CharField(blank=True, editable=False, max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_id',
            field=models.CharField(blank=True, editable=False, max_length=10, unique=True),
        ),
    ]
