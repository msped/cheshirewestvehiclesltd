from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

SchemaView = get_schema_view(
    openapi.Info(
        title="Cheshire West Vehicle API",
        default_version='v1',
        description="Django Rest Framework API for Cheshire West Vehicles.",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include("accounts.urls"), name="accounts_urls"),
    path('api/sales/', include('sales.urls'), name="sales_urls"),
    path('api/gallery/', include('gallery.urls'), name="gallery_urls"),
    path('api/admin/', include('business_admin.urls'), name="admin_urls"),
    path("", SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
