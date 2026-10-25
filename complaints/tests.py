"""Tests for the complaints app. IDs match docs/10_test_plan.md.

Sprint 1: seed data (TC-23 to TC-25). Sprint 2: complaint models and access
rules (TC-36 onwards).
"""

import shutil
import tempfile
from datetime import timedelta
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.http import Http404
from django.test import TestCase, override_settings
from django.utils import timezone

from accounts.models import User
from accounts.permissions import get_complaint_for_user, has_full_view
from notifications.models import Notification

from .management.commands.seed_demo import DEMO_PASSWORD
from .models import (
    MAX_FILE_SIZE,
    Attachment,
    Category,
    Complaint,
    ComplaintUpdate,
    Department,
    Support,
    check_attachment_file,
)

# Smallest byte patterns the filetype library recognises (the file "signature").
FILE_BYTES = {
    "jpg": b"\xff\xd8\xff\xe0" + b"\x00" * 60,
    "png": b"\x89PNG\r\n\x1a\n" + b"\x00" * 60,
    "pdf": b"%PDF-1.4\n" + b"\x00" * 60,
    "mp4": b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom" + b"\x00" * 40,
}


def upload(name, kind=None):
    """A fake uploaded file whose content is a real `kind` file (default: from the name)."""
    kind = kind or name.rsplit(".", 1)[-1].lower()
    return SimpleUploadedFile(name, FILE_BYTES[kind])


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


class ComplaintFixtures(TestCase):
    """Two departments, their admins, a Super Admin and three students.

    Uploaded files go to a temporary MEDIA_ROOT that is deleted afterwards.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_root = tempfile.mkdtemp()
        cls.media_override = override_settings(MEDIA_ROOT=cls.media_root)
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_override.disable()
        shutil.rmtree(cls.media_root, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.it = Department.objects.create(name="IT Services", code="IT")
        cls.fac = Department.objects.create(name="Facilities Management", code="FAC")
        cls.projector = Category.objects.create(name="Projector & AV", department=cls.it)
        cls.network = Category.objects.create(name="Network", department=cls.it)
        cls.electrical = Category.objects.create(
            name="Electrical", department=cls.fac, requires_attachment=True
        )

        def user(email, role=User.Role.STUDENT, **extra):
            if role == User.Role.STUDENT:
                extra.setdefault("student_id", email.split("@")[0])
            return User.objects.create_user(f"{email}@northsouth.edu", "pw", full_name=email, role=role, **extra)

        cls.it_admin = user("it.admin", User.Role.DEPT_ADMIN, department=cls.it)
        cls.fac_admin = user("fac.admin", User.Role.DEPT_ADMIN, department=cls.fac)
        cls.boss = user("boss", User.Role.SUPER_ADMIN)
        cls.reporter = user("reporter")
        cls.other = user("other")
        cls.stranger = user("stranger")

    def submit(self, category=None, building="nac", room="512", files=(), reporter=None):
        return Complaint.submit(
            reporter=reporter or self.reporter,
            category=category or self.projector,
            building=building,
            room=room,
            title="Projector shows no signal",
            description="HDMI input is dead.",
            files=files,
        )


class SubmitTests(ComplaintFixtures):
    """C-02, C-04: Complaint.submit() (docs/03 §4 Submit)."""

    def test_tc36_tracking_id_is_uf_plus_padded_primary_key(self):
        first = self.submit()
        second = self.submit()
        self.assertEqual(first.tracking_id, f"UF-{first.pk:04d}")
        self.assertEqual(second.tracking_id, f"UF-{second.pk:04d}")
        self.assertRegex(first.tracking_id, r"^UF-\d{4,}$")

    def test_tc37_submit_routes_records_history_and_notifies_department(self):
        complaint = self.submit(files=[upload("photo.jpg"), upload("manual.pdf")])
        self.assertEqual(complaint.status, Complaint.Status.SUBMITTED)
        self.assertEqual(complaint.department, self.it)  # C-04: copied from the category
        update = complaint.updates.get()
        self.assertEqual(
            (update.action, update.actor, update.to_status),
            (ComplaintUpdate.Action.SUBMITTED, self.reporter, "submitted"),
        )
        files = list(complaint.attachments.all())
        self.assertEqual([f.original_name for f in files], ["photo.jpg", "manual.pdf"])
        self.assertEqual([f.mime_type for f in files], ["image/jpeg", "application/pdf"])
        self.assertTrue(files[0].file.name.startswith(f"complaints/{complaint.tracking_id}/"))
        self.assertNotIn("photo", files[0].file.name)  # random name on disk
        # Only the admins of the routed department are notified.
        self.assertEqual(
            list(Notification.objects.values_list("recipient", "event")),
            [(self.it_admin.pk, Notification.Event.NEW_COMPLAINT)],
        )

    def test_tc38_vr07_rejects_wrong_type_mismatch_size_and_count(self):
        with self.assertRaisesMessage(ValidationError, "only JPG"):
            check_attachment_file(SimpleUploadedFile("clip.gif", b"GIF89a"))
        with self.assertRaisesMessage(ValidationError, "does not match"):
            check_attachment_file(upload("photo.jpg", kind="pdf"))  # a PDF renamed to .jpg
        big = upload("photo.jpg")
        big.size = MAX_FILE_SIZE + 1
        with self.assertRaisesMessage(ValidationError, "15 MB"):
            check_attachment_file(big)
        self.assertEqual(check_attachment_file(upload("CLIP.MP4")), "video/mp4")
        with self.assertRaisesMessage(ValidationError, "at most 5"):
            self.submit(files=[upload(f"p{i}.png") for i in range(6)])
        # A bad file in the batch: nothing is saved.
        with self.assertRaises(ValidationError):
            self.submit(files=[upload("ok.png"), upload("bad.png", kind="pdf")])
        self.assertFalse(Complaint.objects.exists())
        self.assertFalse(Attachment.objects.exists())

    def test_tc39_vr08_category_requiring_attachment_needs_a_file(self):
        with self.assertRaisesMessage(ValidationError, "at least one"):
            self.submit(category=self.electrical)
        self.assertFalse(Complaint.objects.exists())
        complaint = self.submit(category=self.electrical, files=[upload("socket.jpg")])
        self.assertEqual(complaint.department, self.fac)
        self.assertEqual(self.submit(category=self.network).attachments.count(), 0)  # not required

    def test_tc40_only_students_and_active_categories(self):
        with self.assertRaises(ValidationError):
            self.submit(reporter=self.it_admin)
        self.network.is_active = False
        self.network.save()
        with self.assertRaisesMessage(ValidationError, "no longer available"):
            self.submit(category=self.network)


class DuplicateRuleTests(ComplaintFixtures):
    """docs/03 §6: same category, building, room (normalised) and an open status."""

    def test_tc41_duplicate_rule(self):
        match = self.submit(room="L 3")
        self.submit(room="L4")  # other room
        self.submit(building="sac", room="L3")  # other building
        self.submit(category=self.network, room="L3")  # other category
        closed = self.submit(room="l3")
        Complaint.objects.filter(pk=closed.pk).update(status=Complaint.Status.CLOSED)
        blank_room = self.submit(room="")

        found = Complaint.find_duplicates(self.projector, "nac", "l3")
        self.assertEqual(sorted(c.pk for c in found), sorted([match.pk, blank_room.pk]))
        # A blank room compares the building only: L 3, L4 and the blank one (not the closed one).
        self.assertEqual(len(Complaint.find_duplicates(self.projector, "nac", "")), 3)


class SupportTests(ComplaintFixtures):
    """C-03, VR-09: "Me too"."""

    def test_tc42_support_writes_support_and_history(self):
        complaint = self.submit()
        before = complaint.updated_at
        complaint.support(self.other)
        self.assertTrue(Support.objects.filter(complaint=complaint, student=self.other).exists())
        update = complaint.updates.last()
        self.assertEqual((update.action, update.actor), (ComplaintUpdate.Action.SUPPORT, self.other))
        complaint.refresh_from_db()
        self.assertGreater(complaint.updated_at, before)
        self.assertEqual((complaint.support_count, complaint.affected_count), (1, 2))

    def test_tc43_vr09_own_twice_closed_or_admin_refused(self):
        complaint = self.submit()
        with self.assertRaisesMessage(ValidationError, "your own"):
            complaint.support(self.reporter)
        complaint.support(self.other)
        with self.assertRaisesMessage(ValidationError, "already support"):
            complaint.support(self.other)
        with self.assertRaises(ValidationError):
            complaint.support(self.it_admin)
        complaint.status = Complaint.Status.REJECTED
        with self.assertRaisesMessage(ValidationError, "open complaints"):
            complaint.support(self.stranger)
        self.assertEqual(complaint.supports.count(), 1)


class ComputedValueTests(ComplaintFixtures):
    """docs/03 §5 and the display helpers in docs/05 §3."""

    def test_tc44_computed_properties(self):
        complaint = self.submit(room="512")
        today = timezone.localdate()
        self.assertEqual(complaint.location, "NAC 512")
        complaint.status = Complaint.Status.UNDER_REVIEW
        self.assertEqual(complaint.status_badge_class, "badge-under-review")

        complaint.due_date = today - timedelta(days=1)
        self.assertFalse(complaint.is_overdue)  # under review: never overdue
        for status in ["verified", "in_progress", "reopened"]:
            complaint.status = status
            self.assertTrue(complaint.is_overdue)
        complaint.status = "resolved"
        self.assertFalse(complaint.is_overdue)

        complaint.resolved_at = timezone.now() - timedelta(days=7)
        self.assertTrue(complaint.can_reopen)
        complaint.resolved_at = timezone.now() - timedelta(days=8)
        self.assertFalse(complaint.can_reopen)


class ComplaintAccessTests(ComplaintFixtures):
    """VR-01, VR-02: User.can_view_complaint() and the permission helpers."""

    def test_tc45_can_view_complaint_for_each_role(self):
        complaint = self.submit()
        complaint.support(self.other)
        allowed = {
            self.reporter: True,
            self.other: True,  # supporter (limited view)
            self.stranger: False,
            self.it_admin: True,  # own department
            self.fac_admin: False,  # VR-02
            self.boss: True,
        }
        for user, expected in allowed.items():
            with self.subTest(user=user.full_name):
                self.assertEqual(user.can_view_complaint(complaint), expected)

    def test_tc46_helpers_give_404_and_limited_view(self):
        complaint = self.submit()
        complaint.support(self.other)
        self.assertEqual(get_complaint_for_user(self.reporter, complaint.tracking_id), complaint)
        for user in [self.stranger, self.fac_admin]:
            with self.assertRaises(Http404):
                get_complaint_for_user(user, complaint.tracking_id)
        with self.assertRaises(Http404):
            get_complaint_for_user(self.reporter, "UF-9999")
        self.assertTrue(has_full_view(self.reporter, complaint))
        self.assertFalse(has_full_view(self.other, complaint))  # supporter: limited
        self.assertTrue(has_full_view(self.it_admin, complaint))
        self.assertFalse(has_full_view(self.fac_admin, complaint))
