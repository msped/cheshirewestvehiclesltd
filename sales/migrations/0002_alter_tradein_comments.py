# Generated by Django 4.1.4 on 2022-12-22 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradein',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
    ]
