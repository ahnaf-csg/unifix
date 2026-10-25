from django.apps import AppConfig


class ConsoleConfig(AppConfig):
    """Admin-side views: dashboard, queue, actions, students, users, reports (docs/05 §2).

    The console has no models of its own; it works on models from the other apps.
    """

    name = "console"
