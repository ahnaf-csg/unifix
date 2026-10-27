"""Root URL configuration. URL names and paths follow docs/05 §4."""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    # "/" sends everyone to the login page, which forwards signed-in users to their home.
    path("", RedirectView.as_view(pattern_name="accounts:login")),
    path("", include("accounts.urls")),
    path("student/", include("complaints.urls")),
    path("console/", include("console.urls")),
    path("notifications/", include("notifications.urls")),
    # Django admin stays at /django-admin/ to avoid confusion with the console.
    path("django-admin/", admin.site.urls),
]
