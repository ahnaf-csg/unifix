"""Complaint models (docs/05 §3).

Sprint 1 adds only Department and Category, which are managed in the Django
admin panel (C-16). Complaint, Attachment, ComplaintUpdate, Support and Rating
follow in Sprints 2 to 4.
"""

from django.db import models


class Department(models.Model):
    """A campus department that handles complaints, e.g. Facilities Management."""

    name = models.CharField(max_length=80, unique=True)
    code = models.CharField(max_length=10, unique=True)  # e.g. FAC, IT, HK, SEC
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    """A complaint category. Its department is where new complaints are routed (C-04)."""

    name = models.CharField(max_length=80)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="categories"
    )
    requires_attachment = models.BooleanField(default=False)  # VR-08
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["department__name", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
