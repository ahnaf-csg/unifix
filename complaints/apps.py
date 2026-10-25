from django.apps import AppConfig


class ComplaintsConfig(AppConfig):
    """Departments, categories, complaints and student-facing views (docs/05 §2)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "complaints"
