"""Tests for the complaints app (Sprint 1: seed data). IDs match docs/10_test_plan.md."""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from accounts.models import User

from .management.commands.seed_demo import DEMO_PASSWORD
from .models import Category, Department


class SeedDemoTests(TestCase):
    def seed(self):
        call_command("seed_demo", stdout=StringIO())

    def test_tc23_seed_creates_docs_05_data(self):
        self.seed()
        self.assertEqual(
            sorted(Department.objects.values_list("code", flat=True)), ["FAC", "HK", "IT", "SEC"]
        )
        self.assertEqual(Category.objects.count(), 11)
        self.assertTrue(Category.objects.get(name="Electrical").requires_attachment)
        self.assertFalse(Category.objects.get(name="Network").requires_attachment)
        self.assertEqual(User.objects.filter(role=User.Role.SUPER_ADMIN).count(), 1)
        for department in Department.objects.all():
            self.assertEqual(department.admins.filter(role=User.Role.DEPT_ADMIN).count(), 1)
        self.assertEqual(User.objects.filter(role=User.Role.STUDENT).count(), 10)

    def test_tc24_seed_can_run_twice_without_duplicates(self):
        self.seed()
        self.seed()
        self.assertEqual(Department.objects.count(), 4)
        self.assertEqual(Category.objects.count(), 11)
        self.assertEqual(User.objects.count(), 15)

    def test_tc25_demo_accounts_can_log_in(self):
        self.seed()
        self.assertTrue(
            self.client.login(username="rafiq.hasan@northsouth.edu", password=DEMO_PASSWORD)
        )
