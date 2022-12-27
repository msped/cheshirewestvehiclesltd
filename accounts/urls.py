from django.urls import path, include

urlpatterns = [
    path('', include('djoser.urls.jwt')),
    path('', include('djoser.urls')),
]
