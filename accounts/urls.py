from django.urls import path, include

from .views import ChangePasswordView

urlpatterns = [
    path('', include('djoser.urls.jwt')),
    path('', include('djoser.urls')),
    path(
        'change-password/',
        ChangePasswordView.as_view(),
        name="change_password"
    ),
]
