from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """User model, login, register, profile and user records (docs/05 §2)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
