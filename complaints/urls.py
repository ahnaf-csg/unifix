"""URL names for the student namespace (docs/05 §4)."""

from django.urls import path

from . import views

app_name = "student"

urlpatterns = [
    path("", views.home, name="home"),
]
