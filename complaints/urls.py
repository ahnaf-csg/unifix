"""URL names for the student namespace (docs/05 §4)."""

from django.urls import path

from . import views

app_name = "student"

urlpatterns = [
    path("", views.home, name="home"),
    path("complaints/", views.complaint_list, name="complaint_list"),
    path("complaints/new/", views.complaint_new, name="complaint_new"),
    path("complaints/<str:tracking_id>/", views.complaint_detail, name="complaint_detail"),
    path("complaints/<str:tracking_id>/files/<int:pk>/", views.attachment, name="attachment"),
    path("complaints/<str:tracking_id>/<slug:action>/", views.complaint_action, name="complaint_action"),
]
