from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include("accounts.urls"), name="accounts_urls"),
    path('api/sales/', include('sales.urls'), name="sales_urls"),
    path('api/gallery/', include('gallery.urls'), name="gallery_urls"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
