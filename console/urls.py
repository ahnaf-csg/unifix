"""URL names for the console namespace (docs/05 §4)."""

from django.urls import path

from . import views

app_name = "console"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]
