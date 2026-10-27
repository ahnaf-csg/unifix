"""Role checks: the one place where permissions are enforced (CLAUDE.md).

Every view that needs a signed-in user uses one of these decorators, so the
check happens on the server whatever the templates show or hide.

    @student_required          only students
    @admin_required            Dept Admins and the Super Admin
    @super_admin_required      only the Super Admin
    @signed_in_required        any role

Complaint access (VR-01, VR-02) is checked by get_complaint_for_user(), which
every complaint page uses to load its complaint.
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect

from complaints.models import Complaint

from .forms import ACCOUNT_INACTIVE_MESSAGE
from .models import User


def role_required(*roles):
    """Allow signed-in, active users whose role is in `roles` (any role if empty)."""

    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            # VR-11: an account suspended while signed in is signed out on its next request.
            if not user.is_active:
                logout(request)
                messages.error(request, ACCOUNT_INACTIVE_MESSAGE)
                return redirect("accounts:login")
            if roles and user.role not in roles:
                raise PermissionDenied  # 403
            return view(request, *args, **kwargs)

        return wrapper

    return decorator


signed_in_required = role_required()
student_required = role_required(User.Role.STUDENT)
admin_required = role_required(User.Role.DEPT_ADMIN, User.Role.SUPER_ADMIN)
super_admin_required = role_required(User.Role.SUPER_ADMIN)


def get_complaint_for_user(user, tracking_id):
    """Load a complaint the user may open, or show 404 (VR-01, VR-02).

    404 rather than 403, so a page never reveals that a tracking ID exists.
    """
    complaint = get_object_or_404(
        Complaint.objects.select_related("reporter", "category", "department"),
        tracking_id=tracking_id,
    )
    if not user.can_view_complaint(complaint):
        raise Http404
    return complaint


def has_full_view(user, complaint):
    """Full view (description, files, reporter): everyone allowed except supporters (VR-01)."""
    if user.is_student():
        return complaint.reporter_id == user.pk
    return user.can_view_complaint(complaint)
