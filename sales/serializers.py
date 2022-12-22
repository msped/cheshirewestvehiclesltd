from rest_framework import serializers
from .models import Vehicle, VehicleImages

class VehicleImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImages
        fields = [
            "id",
            "vehicle",
            "image",
            "order_of_images"
        ]

class VehicleSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    reserved = serializers.CharField(
        source="get_reserved_display"
    )
    car_state = serializers.CharField(
        source="get_car_state_display"
    )
    fuel = serializers.CharField(
        source="get_fuel_display"
    )
    body_type = serializers.CharField(
        source="get_body_type_display"
    )

    def get_images(self, obj):
        images = VehicleImages.objects.filter(vehicle_id=obj.id)
        serializer = VehicleImagesSerializer(images, many=True)
        return serializer.data

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
            "images"
        ]

class VehicleSerializerList(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    reserved = serializers.CharField(
        source="get_reserved_display"
    )
    car_state = serializers.CharField(
        source="get_car_state_display"
    )
    fuel = serializers.CharField(
        source="get_fuel_display"
    )
    body_type = serializers.CharField(
        source="get_body_type_display"
    )

    def get_images(self, obj):
        images = VehicleImages.objects.get(vehicle_id=obj.id, order_of_images=1)
        serializer = VehicleImagesSerializer(images, many=False)
        return serializer.data

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
            "images"
        ]

class VehicleStateSerializer(serializers.ModelSerializer):
    reserved = serializers.CharField(
        source="get_reserved_display"
    )

    class Meta:
        model = Vehicle
        fields = ["id", "reserved"]
