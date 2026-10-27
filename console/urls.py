"""URL names for the console namespace (docs/05 §4)."""

from django.urls import path

from . import views

app_name = "console"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("complaints/", views.queue, name="queue"),
    path("complaints/<str:tracking_id>/", views.complaint_detail, name="complaint_detail"),
    path("complaints/<str:tracking_id>/files/<int:pk>/", views.attachment, name="attachment"),
    path("complaints/<str:tracking_id>/<slug:action>/", views.complaint_action, name="complaint_action"),
]
