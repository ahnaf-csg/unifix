"""Notifications in the Django admin, read-only (for checking data; the list page is Sprint 3)."""

from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["created_at", "recipient", "event", "message", "is_read"]
    list_filter = ["event", "is_read"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
