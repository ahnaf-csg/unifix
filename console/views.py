"""Admin console views, URL namespace `console` (docs/05 §2, §4)."""

from django.shortcuts import render

from accounts.permissions import admin_required
from complaints.models import Department


@admin_required
def dashboard(request):
    """A-01 Dashboard (C-14). Layout preview: cards and tables arrive in Sprint 4, charts in Sprint 5.

    Only the "Categories routed to…" table reads the database; nothing is computed here.

    Dept Admins see their own department; the Super Admin sees all departments (VR-02).
    """
    if request.user.is_super_admin():
        departments = Department.objects.all()
    else:
        departments = Department.objects.filter(pk=request.user.department_id)
    departments = departments.prefetch_related("categories")
    return render(request, "console/dashboard.html", {"departments": departments})
