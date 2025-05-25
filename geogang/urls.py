from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path(settings.ADMINISTRATION_URL[1:], admin.site.urls, name='administration'),
    path('', include('core.urls')),
]
