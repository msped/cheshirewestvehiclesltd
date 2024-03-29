from django.contrib import admin
from .models import Vehicle, VehicleImages, Reservation, TradeIn, ReservationAmount

# Register your models here.

admin.site.register(ReservationAmount)
admin.site.register(Reservation)
admin.site.register(TradeIn)


class VehicleImagesInlineAdmin(admin.TabularInline):
    model = VehicleImages


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    inlines = [VehicleImagesInlineAdmin]

    class Meta:
        model = Vehicle


@admin.register(VehicleImages)
class VehicleImagesAdmin(admin.ModelAdmin):
    pass
