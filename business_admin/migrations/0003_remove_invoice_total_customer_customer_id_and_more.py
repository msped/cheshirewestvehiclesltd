# Generated by Django 4.1.4 on 2023-01-22 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business_admin', '0002_alter_customer_address_line_2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='total',
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_id',
            field=models.CharField(blank=True, editable=False, max_length=9, unique=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='invoice',
            name='labour_quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='invoice',
            name='labour_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='invoice',
            name='labour_unit',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.DeleteModel(
            name='InvoiceLabour',
        ),
    ]
