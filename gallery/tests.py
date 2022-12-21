import shutil
import tempfile
from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from .models import GalleryImage, GalleryItem

# Create your tests here.

MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestGalleryModels(APITestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        return super().tearDownClass()

    def gallery_item(self):
        GalleryItem.objects.create(
            make='Mercedes',
            model='190E',
            trim='Cosworth',
            year=1992,
            description='Test description',
            published=True
        ).save()
        gallery_item = GalleryItem.objects.get(
            make='Mercedes',
            model='190E',
            trim='Cosworth',
            year=1992,
            description='Test description',
            published=True
        )
        self.assertEqual(str(gallery_item), '1 Mercedes 190E Cosworth')
        self.assertEqual(gallery_item.id, 1)
        self.assertEqual(gallery_item.make, 'Mercedes')
        self.assertEqual(gallery_item.model, '190E')
        self.assertEqual(gallery_item.trim, 'Cosworth')
        self.assertEqual(gallery_item.year, 1992)
        self.assertEqual(gallery_item.description, 'Test description')
        self.assertTrue(gallery_item.published)

    def gallery_image(self):
        gallery_item = GalleryItem.objects.get(
            make='Mercedes',
            model='190E',
            trim="Cosworth",
        )
        GalleryImage.objects.create(
            item=gallery_item,
            image=SimpleUploadedFile('image_1.jpg', b'testimageofacar'),
            order_of_images=1
        ).save()
        gallery_image = GalleryImage.objects.get(
            item=gallery_item,
            order_of_images=1
        )
        self.assertEqual(
            str(gallery_image),
            'Order: 1 - (1) Mercedes 190E Cosworth'
        )
        self.assertEqual(gallery_image.item.make, 'Mercedes')
        self.assertEqual(gallery_image.item.model, '190E')
        self.assertEqual(gallery_image.item.trim, 'Cosworth')
        self.assertEqual(gallery_image.image.url, '/media/gallery/image_1.jpg')
        self.assertEqual(gallery_image.order_of_images, 1)

    def test_in_order(self):
        self.gallery_item()
        self.gallery_image()
