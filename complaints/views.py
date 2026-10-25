"""Student-facing views, URL namespace `student` (docs/05 §2, §4)."""

from django.shortcuts import render

from accounts.permissions import student_required


@student_required
def home(request):
    """S-01 Student home. Placeholder until complaints are built in Sprint 2."""
    return render(request, "student/home.html")
