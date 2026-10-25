from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """In-app notifications (C-11). The Notification model is added in Sprint 3."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
