"""Root URL configuration. URL names and paths follow docs/05 §4."""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    # Django admin stays at /django-admin/ to avoid confusion with the console.
    path("django-admin/", admin.site.urls),
]
