"""Tests for the A-01 dashboard layout preview (C-14, Update 1 presentation branch; no TC IDs)."""

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from accounts.tests import make_user
from complaints.models import Category, Department

PLACEHOLDERS = [
    "Arrives in Sprint 4",  # cards and tables
    "Arrives in Sprint 5",  # charts
    "Overdue (by due date)",
    "Due in next 3 days",
    "Most supported",
    "Weekly trend",
]


class DashboardPreviewTests(TestCase):
    """A-01 shows placeholders only, plus the real "Categories routed to…" table."""

    def setUp(self):
        facilities = Department.objects.create(name="Facilities Management", code="FAC")
        it = Department.objects.create(name="IT Services", code="IT")
        Category.objects.create(name="Broken furniture", department=facilities)
        Category.objects.create(name="Wi-Fi problem", department=it)
        self.student = make_user("student@northsouth.edu")
        self.dept_admin = make_user("fac@northsouth.edu", User.Role.DEPT_ADMIN, department=facilities)
        self.super_admin = make_user("boss@northsouth.edu", User.Role.SUPER_ADMIN)

    def get_dashboard(self, user):
        self.client.force_login(user)
        return self.client.get(reverse("console:dashboard"))

    def assert_placeholders(self, response):
        self.assertEqual(response.status_code, 200)
        for text in PLACEHOLDERS:
            self.assertContains(response, text)
        self.assertContains(response, 'disabled title="Arrives in Sprint 3">Open complaint queue')

    def test_dept_admin_sees_placeholders_and_own_department_categories(self):
        response = self.get_dashboard(self.dept_admin)
        self.assert_placeholders(response)
        self.assertContains(response, "Categories routed to your department")
        self.assertContains(response, "Broken furniture")
        self.assertNotContains(response, "Wi-Fi problem")

    def test_super_admin_sees_placeholders_and_all_categories(self):
        response = self.get_dashboard(self.super_admin)
        self.assert_placeholders(response)
        self.assertContains(response, "Categories routed to each department")
        self.assertContains(response, "Broken furniture")
        self.assertContains(response, "Wi-Fi problem")

    def test_student_gets_403(self):
        self.assertEqual(self.get_dashboard(self.student).status_code, 403)
