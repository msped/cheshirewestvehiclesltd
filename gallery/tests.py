import json
import shutil
import tempfile

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
        self.assertEqual(str(gallery_item),
                         f'{gallery_item.id} Mercedes 190E Cosworth')
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
            image=SimpleUploadedFile('image_1.jpg', b'testimageofacar')
        ).save()
        gallery_image = GalleryImage.objects.filter(
            item=gallery_item
        ).first()
        self.assertEqual(
            str(gallery_image),
            f'({gallery_item.id}) Mercedes 190E Cosworth'
        )
        self.assertEqual(gallery_image.item.make, 'Mercedes')
        self.assertEqual(gallery_image.item.model, '190E')
        self.assertEqual(gallery_image.item.trim, 'Cosworth')
        self.assertEqual(gallery_image.image.url, '/media/gallery/image_1.jpg')

    def test_in_order(self):
        self.gallery_item()
        self.gallery_image()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestGalleryApp(APITestCase):

    def setUp(self):
        g_1 = GalleryItem.objects.create(
            id=1,
            make="Mercedes",
            model="A Class",
            trim="A250",
            year=2013,
            description="loads of stuff",
            published=True
        )
        g_1.save()
        g_2 = GalleryItem.objects.create(
            id=2,
            make="Mercedes",
            model="190E",
            trim="Cosworth",
            year=1992,
            description="loads of stuff",
            published=True
        )
        g_2.save()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        return super().tearDownClass()

    def test_gallery_list(self):
        response = self.client.get('/api/gallery/')
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertEqual(
            json.loads(response.content),
            {
                'count': 2,
                'next': None,
                'previous': None,
                'results': [
                    {
                        'id': 2,
                        'slug': 'mercedes-190e-cosworth-1992',
                        'make': 'Mercedes',
                        'model': '190E',
                        'trim': 'Cosworth',
                        'year': 1992,
                        'description': 'loads of stuff',
                        'published': True,
                        'images': []
                    },
                    {
                        'id': 1,
                        'slug': 'mercedes-a-class-a250-2013',
                        'make': 'Mercedes',
                        'model': 'A Class',
                        'trim': 'A250',
                        'year': 2013,
                        'description': 'loads of stuff',
                        'published': True,
                        'images': []
                    }
                ]
            }
        )

    def test_gallery_detail(self):
        response = self.client.get('/api/gallery/mercedes-a-class-a250-2013/')
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertEqual(
            json.loads(response.content),
            {
                'id': 1,
                'slug': 'mercedes-a-class-a250-2013',
                'make': 'Mercedes',
                'model': 'A Class',
                'trim': 'A250',
                'year': 2013,
                'description': 'loads of stuff',
                'published': True,
                'images': []
            }
        )
