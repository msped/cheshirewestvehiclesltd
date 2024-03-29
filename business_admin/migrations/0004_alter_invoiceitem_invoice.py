# Generated by Django 4.1.4 on 2023-02-05 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business_admin', '0003_remove_invoice_total_customer_customer_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceitem',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_item', to='business_admin.invoice'),
        ),
    ]
