import json
import shutil
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import override_settings
from rest_framework.test import APITestCase

from gallery.models import GalleryItem, GalleryImage

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestBusinessAdminGallery(APITestCase):

    def setUp(self):
        user = get_user_model()
        user.objects.create(
            first_name='Harold',
            last_name='Finch',
            username='admin',
            password=make_password('TestP455word!'),
            is_staff=True
        ).save()

    def temporary_image(self):
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file, 'jpeg')
        tmp_file.seek(0)
        return tmp_file

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def get_access_token(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        return access_request.data['access']

    def create_gallery_no_images(self):
        response = self.client.post(
            '/api/admin/gallery/',
            {
                "make": "Ford",
                "model": "Fiesta",
                "trim": "ST",
                "year": 2019,
                "description": "Test description for Fiesta",
                "published": True,
                "uploaded_images": []
            },
            format="multipart",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 201)

    def create_gallery_with_images(self):
        response = self.client.post(
            '/api/admin/gallery/',
            {
                "make": "Nissan",
                "model": "Skyline",
                "trim": "GTR V-spec",
                "year": 2001,
                "description": "Godzilla",
                "published": True,
                "uploaded_images": [
                    self.temporary_image(),
                    self.temporary_image()
                ]
            },
            format="multipart",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 201)
        gallery = GalleryItem.objects.get(
            make="Nissan",
            model="Skyline",
            trim="GTR V-spec",
            year=2001
        )
        self.assertEqual(GalleryImage.objects.filter(
            item_id=gallery.id
        ).count(), 2)

    def get_gallery(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        response = self.client.get(
            '/api/admin/gallery/ford-fiesta-st-2019/',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)

    def update_gallery_with_images(self):
        gallery = GalleryItem.objects.get(
            make="Nissan",
            model="Skyline",
            trim="GTR V-spec",
            year=2001
        )
        response = self.client.patch(
            f'/api/admin/gallery/{gallery.slug}/',
            {
                "make": "Nissan",
                "model": "Skyline",
                "trim": "GTR V-spec",
                "year": 2001,
                "description": "Godzilla",
                "published": True,
                "uploaded_images": [
                    self.temporary_image(),
                    self.temporary_image()
                ]
            },
            format="multipart",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(GalleryImage.objects.filter(
            item_id=gallery.id
        ).count(), 4)

    def update_gallery_without_images(self):
        gallery = GalleryItem.objects.get(
            make="Nissan",
            model="Skyline",
            trim="GTR V-spec",
            year=2001
        )
        response = self.client.patch(
            f'/api/admin/gallery/{gallery.slug}/',
            {
                "make": "Nissan",
                "model": "Skyline",
                "trim": "GTR V-spec",
                "year": 2000,
                "description": "A proper description",
                "published": True,
                "uploaded_images": []
            },
            format="multipart",
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(GalleryImage.objects.filter(
            item_id=gallery.id
        ).count(), 4)
        json_response = json.loads(response.content)
        self.assertEqual(json_response['year'], 2000)
        self.assertEqual(json_response['description'], 'A proper description')

    def delete_gallery_image(self):
        image = GalleryImage.objects.filter(
            item__slug="nissan-skyline-gtr-v-spec-2000"
        ).first()
        response = self.client.delete(
            f'/api/admin/gallery/image/{image.id}/',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(GalleryImage.objects.filter(
            item_id=image.item.id
        ).count(), 3)

    def delete_gallery(self):
        access_request = self.client.post(
            '/api/auth/jwt/create/',
            {
                'username': 'admin',
                'password': 'TestP455word!'
            }
        )
        access_token = access_request.data['access']
        response = self.client.delete(
            '/api/admin/gallery/ford-fiesta-st-2019/',
            **{'HTTP_AUTHORIZATION': f'Bearer {self.get_access_token()}'}
        )
        self.assertEqual(response.status_code, 204)

    def test_in_order(self):
        self.create_gallery_no_images()
        self.create_gallery_with_images()
        self.get_gallery()
        self.update_gallery_with_images()
        self.update_gallery_without_images()
        self.delete_gallery_image()
        self.delete_gallery()
