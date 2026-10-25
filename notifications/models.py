"""In-app notifications (docs/05 §3 notifications.Notification, C-11).

Sprint 2 builds the model so that Complaint.submit() can notify department
admins. The list page and the bell's unread count come in Sprint 3.
"""

from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Event(models.TextChoices):
        NEW_COMPLAINT = "new_complaint", "New complaint"
        STATUS_CHANGED = "status_changed", "Status changed"
        NOTE_ADDED = "note_added", "Note added"
        REOPENED = "reopened", "Reopened"
        REASSIGNED = "reassigned", "Reassigned"
        RATED = "rated", "Rated"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    # A string reference, because complaints.models imports this module.
    complaint = models.ForeignKey(
        "complaints.Complaint",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    event = models.CharField(max_length=20, choices=Event.choices)
    message = models.CharField(max_length=255)  # e.g. "UF-1042 was marked Resolved"
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]

    def __str__(self):
        return self.message
