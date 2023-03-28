from rest_framework import serializers
from .models import Vehicle, VehicleImages


class VehicleImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImages
        fields = [
            "id",
            "vehicle",
            "image",
        ]


class VehicleSerializer(serializers.ModelSerializer):
    images = VehicleImagesSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.FileField(
            max_length=1000000,
            allow_empty_file=False,
            use_url=False
        ),
        write_only=True,
        required=False
    )

    reserved = serializers.CharField(
        source="get_reserved_display",
        read_only=True
    )
    car_state = serializers.CharField(
        source="get_car_state_display",
        read_only=True
    )
    fuel = serializers.CharField(
        source="get_fuel_display",
        read_only=True
    )
    body_type = serializers.CharField(
        source="get_body_type_display",
        read_only=True
    )

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "slug",
            "make",
            "model",
            "trim",
            "year",
            "fuel",
            "body_type",
            "car_state",
            "reserved",
            "mileage",
            "engine_size",
            "mot_expiry",
            "extras",
            "price",
            'published',
            'images',
            'uploaded_images',
        ]

    def create(self, validated_data):
        if 'uploaded_images' in validated_data:
            uploaded_images = validated_data.pop('uploaded_images')
            vehicle = Vehicle.objects.create(**validated_data)
            for image in uploaded_images:
                VehicleImages.objects.create(
                    vehicle_id=vehicle.id,
                    image=image
                )
        else:
            vehicle = Vehicle.objects.create(**validated_data)
        return vehicle

    def update(self, instance, validated_data):
        if 'uploaded_images' in validated_data:
            uploaded_images = validated_data.pop('uploaded_images')
            for image in uploaded_images:
                VehicleImages.objects.create(
                    vehicle_id=instance.id,
                    image=image
                )
        super().update(instance, validated_data)
        return instance


class VehicleStateSerializer(serializers.ModelSerializer):
    reserved = serializers.CharField(
        source="get_reserved_display"
    )

    class Meta:
        model = Vehicle
        fields = ["id", "reserved"]
