from django.contrib import admin
from .models import Vehicle, VehicleImages, Reservations, TradeIn

# Register your models here.

admin.site.register(Reservations)
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
