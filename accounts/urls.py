"""URL names for the accounts namespace (docs/05 §4)."""

from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.UniFixLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),  # POST only
    path("register/", views.register, name="register"),
]
