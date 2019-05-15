"""
djapi_maker URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('deviceapi', include('device.urls'), name='deviceapi'),
    path('api/', include('api.urls'), name='api_urls'),
]
