# Generated by Django 4.1.4 on 2022-12-18 18:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('make', models.CharField(max_length=45)),
                ('model', models.CharField(max_length=45)),
                ('trim', models.CharField(max_length=45)),
                ('year', models.IntegerField()),
                ('description', models.TextField()),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='GalleryImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='gallery')),
                ('order_of_images', models.IntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gallery.galleryitem')),
            ],
            options={
                'ordering': ['order_of_images'],
            },
        ),
    ]
