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
        ]


class GallerySerializer(serializers.ModelSerializer):
    """Serializer for a full gallery item"""
    images = serializers.SerializerMethodField()
    uploaded_images = serializers.ListField(
        child=serializers.FileField(
            max_length=1000000,
            allow_empty_file=False,
            use_url=False
        ),
        write_only=True,
        required=False
    )

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
            'images',
            'uploaded_images',
        ]

    def get_images(self, obj):
        images = GalleryImage.objects.filter(item_id=obj.id)
        serializer = GalleryImageSerializer(images, many=True)
        return serializer.data

    def create(self, validated_data):
        if 'uploaded_images' in validated_data:
            uploaded_images = validated_data.pop('uploaded_images')
            gallery = GalleryItem.objects.create(**validated_data)
            for image in uploaded_images:
                GalleryImage.objects.create(
                    item_id=gallery.id,
                    image=image
                )
        else:
            gallery = GalleryItem.objects.create(**validated_data)
        return gallery

    def update(self, instance, validated_data):
        if 'uploaded_images' in validated_data:
            uploaded_images = validated_data.pop('uploaded_images')
            for image in uploaded_images:
                GalleryImage.objects.create(
                    item_id=instance.id,
                    image=image
                )
        super().update(instance, validated_data)
        return instance
