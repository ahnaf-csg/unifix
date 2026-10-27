"""Notifications list and "Mark all as read" (S-05, A-06, C-11). Shared by all roles."""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.permissions import signed_in_required


def complaint_link(user, complaint):
    """Where a notification about `complaint` leads: S-04 for students, A-03 for admins."""
    if complaint is None:
        return ""
    name = "student:complaint_detail" if user.is_student() else "console:complaint_detail"
    return reverse(name, args=[complaint.tracking_id])


def with_links(user, notifications):
    """Notifications with a `link` attribute each, for the templates."""
    notifications = list(notifications)
    for notification in notifications:
        notification.link = complaint_link(user, notification.complaint)
    return notifications


@signed_in_required
def notification_list(request):
    """S-05 / A-06: own notifications, newest first. Opening the page marks nothing read."""
    notifications = request.user.notifications.select_related("complaint")
    return render(
        request,
        "notifications/list.html",
        {"notifications": with_links(request.user, notifications)},
    )


@signed_in_required
@require_POST
def mark_all_read(request):
    updated = request.user.notifications.filter(is_read=False).update(is_read=True)
    if updated:
        messages.success(request, "All notifications marked as read.")
    return redirect("notifications:list")
