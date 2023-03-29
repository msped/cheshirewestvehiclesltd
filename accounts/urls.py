from django.urls import path, include

from .views import ChangePasswordView, BlacklistTokenView

urlpatterns = [
    path('', include('djoser.urls.jwt')),
    path('', include('djoser.urls')),
    path('jwt/blacklist/', BlacklistTokenView.as_view(), name="logout"),
    path(
        'change-password/',
        ChangePasswordView.as_view(),
        name="change_password"
    ),
]
