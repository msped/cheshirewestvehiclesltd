from rest_framework import serializers

from .models import GalleryImage, GalleryItem

class GalleryItemSerailizer(serializers.ModelSerializer):
    """Serializer for a Gallery Item"""
    slug = serializers.ReadOnlyField()

    class Meta:
        model = GalleryItem
        fields = [
            'id',
            'slug',
            'make',
            'model',
            'trim',
            'year',
            'description',
            'published',
        ]

class GalleryImageSerializer(serializers.ModelSerializer):
    """Serializer for an Image item"""
    class Meta:
        model = GalleryImage
        fields = [
            'id',
            'item',
            'image',
            'order_of_image',
        ]

class GallerySerializer(serializers.ModelSerializer):
    """Serializer for a full gallery item"""
    slug = serializers.ReadOnlyField()

    class Meta:
        model = GalleryItem
        fields = [
            'id'
            'slug',
            'make',
            'model',
            'trim',
            'year',
            'description',
            'published',
            'images',
        ]

        def get_images(self, obj):
            images = GalleryImage.objects.filter(item_id=obj.id)
            serializer = GalleryImageSerializer(images, many=True)
            return serializer.data
