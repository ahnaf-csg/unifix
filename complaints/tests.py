"""Tests for the complaints app. IDs match docs/10_test_plan.md.

Sprint 1: seed data (TC-23 to TC-25). Sprint 2: complaint models and access
rules (TC-36 to TC-61). Sprint 3: workflow methods (TC-64 onwards).
"""

import os
import shutil
import tempfile
from datetime import timedelta
from io import StringIO
from unittest import mock

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.http import Http404
from django.test import TestCase, override_settings
from django.urls import reverse, reverse_lazy
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


class TempMediaMixin:
    """Uploaded files go to a temporary MEDIA_ROOT that is deleted afterwards."""

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


class SeedDemoTests(TempMediaMixin, TestCase):
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

    def test_tc49_seed_complaints_cover_every_status_with_consistent_history(self):
        self.seed()
        self.assertEqual(
            set(Complaint.objects.values_list("status", flat=True)), set(Complaint.Status.values)
        )
        complaints = list(Complaint.objects.all())
        self.assertTrue(any(c.is_overdue for c in complaints))
        self.assertTrue(any(c.status == "reopened" and c.reopen_count == 1 for c in complaints))
        self.assertTrue(Support.objects.exists())
        for complaint in complaints:
            with self.subTest(complaint=complaint.tracking_id):
                updates = list(complaint.updates.all())
                self.assertEqual(updates[0].action, ComplaintUpdate.Action.SUBMITTED)
                self.assertEqual(updates[0].created_at, complaint.created_at)
                times = [u.created_at for u in updates]
                self.assertEqual(times, sorted(times))
                self.assertEqual(updates[-1].to_status, complaint.status)
                if complaint.category.requires_attachment:
                    self.assertTrue(complaint.attachments.exists())  # VR-08 holds for seed data too
                # Sprint 3: steps ran through the real methods at their own time, so each
                # notification has the time of the history row that caused it.
                update_times = {u.created_at for u in updates}
                for notification in complaint.notifications.all():
                    self.assertIn(notification.created_at, update_times)
        # Resolve with a proof photo, and the "reopen by" date counted from resolved_at (docs/03 §4).
        projector = Complaint.objects.get(title="Projector shows no signal")
        self.assertEqual(projector.attachments.filter(kind=Attachment.Kind.PROOF_OF_FIX).count(), 1)
        reopen_by = timezone.localdate(projector.resolved_at) + timedelta(days=7)
        self.assertTrue(projector.notifications.filter(
            message=f"{projector.tracking_id} was resolved. Please confirm or reopen by {reopen_by.day} {reopen_by:%b %Y}"
        ).exists())
        # Running it again adds nothing.
        counts = (Complaint.objects.count(), Attachment.objects.count(), Notification.objects.count())
        self.seed()
        self.assertEqual(
            (Complaint.objects.count(), Attachment.objects.count(), Notification.objects.count()), counts
        )


class ComplaintFixtures(TempMediaMixin, TestCase):
    """Two departments, their admins, a Super Admin and three students."""

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
            return User.objects.create_user(f"{email}@northsouth.edu", "pw", full_name=f"Name {email}", role=role, **extra)

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

    def stored_file_count(self):
        return sum(len(files) for _, _, files in os.walk(self.media_root))

    def test_tc47_checked_file_is_stored_unchanged(self):
        photo = upload("photo.jpg")
        check_attachment_file(photo)
        check_attachment_file(photo)  # reading the header twice must not move the start
        complaint = self.submit(files=[photo])
        with complaint.attachments.get().file.open("rb") as stored:
            self.assertEqual(stored.read(), FILE_BYTES["jpg"])

    def test_tc48_failed_submit_leaves_no_files_on_disk(self):
        before = self.stored_file_count()
        with mock.patch.object(Notification.objects, "bulk_create", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                self.submit(files=[upload("a.jpg"), upload("b.pdf")])  # fails after the files are written
        self.assertFalse(Complaint.objects.exists())  # database rolled back
        self.assertEqual(self.stored_file_count(), before)  # and the files removed

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


class NewComplaintPageTests(ComplaintFixtures):
    """S-02: the two-step form (docs/03 §6), C-02, C-03, VR-07, VR-08."""

    url = reverse_lazy("student:complaint_new")

    def setUp(self):
        self.client.force_login(self.reporter)

    def check(self, category=None, building="nac", room="512"):
        category = category or self.projector
        return self.client.get(
            self.url, {"step": "check", "category": category.pk, "building": building, "room": room}
        )

    def post(self, category=None, files=(), **extra):
        data = {
            "category": (category or self.projector).pk,
            "building": "nac",
            "room": "512",
            "title": "Projector flickers",
            "description": "It flickers every few minutes.",
            "attachments": list(files),
            **extra,
        }
        return self.client.post(self.url, data)

    def test_tc50_step_one_lists_active_categories_grouped_by_department(self):
        self.network.is_active = False
        self.network.save()
        response = self.client.get(self.url)
        self.assertContains(response, '<optgroup label="IT Services">')
        self.assertContains(response, "Projector &amp; AV")
        self.assertNotContains(response, ">Network<")
        self.assertContains(response, "Check for similar issues")

    def test_tc51_check_without_matches_opens_step_two(self):
        response = self.check()
        self.assertContains(response, "Details and files")
        self.assertContains(response, 'type="hidden" name="category"')
        self.assertContains(response, "Change")
        self.assertFalse(Complaint.objects.exists())  # nothing saved between steps

    def test_tc52_check_with_matches_shows_limited_summaries_and_labels(self):
        theirs = self.submit(reporter=self.other)
        mine = self.submit(room="5 12")  # the same room, written differently
        supported = self.submit(reporter=self.stranger)
        supported.support(self.reporter)
        response = self.check()
        self.assertContains(response, "Similar open complaints found")
        self.assertContains(response, reverse("student:complaint_action", args=[theirs.tracking_id, "support"]))
        self.assertContains(response, "You reported this")
        self.assertContains(response, "You support this")
        self.assertNotContains(response, reverse("student:complaint_action", args=[mine.tracking_id, "support"]))
        self.assertNotContains(response, "HDMI input is dead.")  # no description (VR-01)
        self.assertNotContains(response, self.other.full_name)  # no reporter (VR-01)
        self.assertContains(response, "Continue with a new complaint")

    def test_tc53_submit_creates_complaint_without_repeating_the_check(self):
        self.submit(reporter=self.other)  # an open match exists
        response = self.post(files=[upload("photo.jpg")])
        complaint = Complaint.objects.get(reporter=self.reporter)
        self.assertRedirects(response, reverse("student:complaint_detail", args=[complaint.tracking_id]))
        self.assertEqual((complaint.department, complaint.attachments.count()), (self.it, 1))

    def test_tc54_submit_errors_vr07_vr08_and_changed_location(self):
        response = self.post(files=[upload("photo.jpg", kind="pdf")])
        self.assertContains(response, "does not match")
        response = self.post(files=[upload(f"p{i}.png") for i in range(6)])
        self.assertContains(response, "at most 5 files")
        response = self.post(category=self.electrical)
        self.assertContains(response, "needs at least one")
        self.assertFalse(Complaint.objects.exists())
        self.network.is_active = False
        self.network.save()
        response = self.post(category=self.network)  # deactivated between the steps
        self.assertRedirects(response, self.url)
        self.assertFalse(Complaint.objects.exists())


class MeTooTests(ComplaintFixtures):
    """C-03, VR-09 through student:complaint_action."""

    def test_tc55_me_too_post_only_and_limited_view_after(self):
        complaint = self.submit()
        url = reverse("student:complaint_action", args=[complaint.tracking_id, "support"])
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url)
        self.assertRedirects(response, reverse("student:complaint_detail", args=[complaint.tracking_id]))
        self.assertTrue(complaint.supports.filter(student=self.other).exists())
        response = self.client.post(url, follow=True)  # twice
        self.assertContains(response, "already support")
        rate_url = reverse("student:complaint_action", args=[complaint.tracking_id, "rate"])
        self.assertEqual(self.client.post(rate_url).status_code, 404)  # arrives in Sprint 4
        self.client.force_login(self.reporter)
        response = self.client.post(url, follow=True)
        self.assertContains(response, "your own complaint")


class ComplaintDetailTests(ComplaintFixtures):
    """S-04, VR-01, NFR-03."""

    def setUp(self):
        self.complaint = self.submit(files=[upload("photo.jpg")])
        self.complaint.support(self.other)
        self.complaint.updates.create(actor=self.it_admin, action="note", note="Public note from IT.")
        self.complaint.updates.create(actor=self.it_admin, action="note", note="Internal only.", is_internal=True)
        self.url = reverse("student:complaint_detail", args=[self.complaint.tracking_id])
        attachment = self.complaint.attachments.get()
        self.file_url = reverse("student:attachment", args=[self.complaint.tracking_id, attachment.pk])

    def test_tc56_reporter_full_view_without_names(self):
        self.client.force_login(self.reporter)
        response = self.client.get(self.url)
        self.assertContains(response, "HDMI input is dead.")
        self.assertContains(response, self.file_url)
        self.assertContains(response, "Public note from IT.")
        self.assertNotContains(response, "Internal only.")
        self.assertContains(response, "IT Services")  # the admin is shown by department
        for name in [self.it_admin.full_name, self.other.full_name]:
            self.assertNotContains(response, name)  # never a person's name (VR-01)

    def test_tc57_supporter_limited_view_stranger_404_admin_403(self):
        self.client.force_login(self.other)
        response = self.client.get(self.url)
        self.assertContains(response, self.complaint.title)
        self.assertContains(response, "limited view")
        self.assertNotContains(response, "HDMI input is dead.")
        self.assertNotContains(response, self.file_url)
        self.assertNotContains(response, self.reporter.full_name)
        self.assertContains(response, "Reporter")
        self.client.force_login(self.stranger)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.client.force_login(self.it_admin)
        self.assertEqual(self.client.get(self.url).status_code, 403)  # admins use the console (Sprint 3)

    def test_tc58_files_only_through_the_checked_view(self):
        self.client.force_login(self.reporter)
        response = self.client.get(self.file_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/jpeg")
        self.assertEqual(b"".join(response.streaming_content), FILE_BYTES["jpg"])
        for user in [self.other, self.stranger]:  # supporter (limited view) and stranger
            self.client.force_login(user)
            self.assertEqual(self.client.get(self.file_url).status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.get(self.file_url).status_code, 302)  # to login
        self.client.force_login(self.reporter)
        stored = self.complaint.attachments.get().file.name
        self.assertEqual(self.client.get(f"/media/{stored}").status_code, 404)  # no public route


class StudentListPageTests(ComplaintFixtures):
    """S-01 and S-03."""

    def test_tc59_my_complaints_lists_own_and_supported_with_filter_and_search(self):
        own = self.submit(room="512")
        supported = self.submit(reporter=self.other, room="L3")
        supported.support(self.reporter)
        hidden = self.submit(reporter=self.stranger)
        Complaint.objects.filter(pk=own.pk).update(status=Complaint.Status.UNDER_REVIEW)
        self.client.force_login(self.reporter)
        url = reverse("student:complaint_list")
        response = self.client.get(url)
        self.assertContains(response, own.tracking_id)
        self.assertContains(response, supported.tracking_id)
        self.assertContains(response, "Supported")
        self.assertNotContains(response, hidden.tracking_id)
        response = self.client.get(url, {"status": "under_review"})
        self.assertContains(response, own.tracking_id)
        self.assertNotContains(response, supported.tracking_id)
        for query in ["l3", supported.tracking_id.lower()]:
            response = self.client.get(url, {"q": query})
            self.assertContains(response, supported.tracking_id)
            self.assertNotContains(response, own.tracking_id)
        response = self.client.get(url, {"q": hidden.tracking_id})
        self.assertContains(response, "No complaints match")  # VR-14: no results, not an error
        self.assertNotContains(response, reverse("student:complaint_detail", args=[hidden.tracking_id]))

    def test_tc60_home_cards_and_sidebar_links(self):
        open_one = self.submit()
        resolved = self.submit()
        Complaint.objects.filter(pk=resolved.pk).update(status="resolved", resolved_at=timezone.now())
        self.submit(reporter=self.other).support(self.reporter)
        self.client.force_login(self.reporter)
        response = self.client.get(reverse("student:home"))
        counts = [response.context[key] for key in ["open_count", "awaiting_count", "closed_count", "supported_count"]]
        self.assertEqual(counts, [1, 1, 0, 1])
        self.assertContains(response, open_one.tracking_id)
        self.assertContains(response, f'href="{reverse("student:complaint_new")}"')
        self.assertContains(response, f'href="{reverse("student:complaint_list")}"')


class DjangoAdminTests(ComplaintFixtures):
    """C-16: complaints are shown read-only in the Django admin."""

    def test_tc61_super_admin_opens_complaint_read_only(self):
        complaint = self.submit(files=[upload("photo.jpg")])
        complaint.support(self.other)
        self.client.force_login(self.boss)
        response = self.client.get(reverse("admin:complaints_complaint_change", args=[complaint.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "photo.jpg")  # attachment inline, shown as text
        self.assertNotContains(response, 'type="submit" value="Save"')  # view only
        self.assertNotContains(response, "/delete/")  # no Delete button
        delete_url = reverse("admin:complaints_complaint_delete", args=[complaint.pk])
        self.assertEqual(self.client.post(delete_url, {"post": "yes"}).status_code, 403)
        self.assertTrue(Complaint.objects.filter(pk=complaint.pk).exists())
        self.assertEqual(self.client.get(reverse("admin:complaints_complaint_changelist")).status_code, 200)


# --- Sprint 3: workflow methods (docs/03 §2, §4) ------------------------------


class WorkflowFixtures(ComplaintFixtures):
    def at_status(self, status, **fields):
        """A submitted IT complaint moved straight to `status` (test set-up only)."""
        complaint = self.submit()
        Complaint.objects.filter(pk=complaint.pk).update(status=status, **fields)
        complaint.refresh_from_db()
        return complaint

    def tomorrow(self):
        return timezone.localdate() + timedelta(days=1)

    def run_action(self, complaint, action, actor):
        """Call one action method with valid input."""
        inputs = {
            "start_review": {},
            "verify": {"priority": "high", "due_date": self.tomorrow()},
            "reject": {"reason": "Out of scope"},
            "start_work": {},
            "resolve": {"note": "Fixed"},
        }
        getattr(complaint, action)(actor, **inputs[action])


class WorkflowTests(WorkflowFixtures):
    """C-05 to C-08, C-10: the Sprint 3 action methods (TC-64 to TC-74)."""

    def test_tc64_full_path_writes_history_and_notifies_reporter(self):
        complaint = self.submit()
        complaint.start_review(self.it_admin)
        complaint.verify(self.it_admin, "high", self.tomorrow())
        complaint.start_work(self.it_admin, note="Ordering a cable")
        complaint.resolve(self.it_admin, "Cable replaced")
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, "resolved")
        self.assertEqual((complaint.priority, complaint.due_date), ("high", self.tomorrow()))
        self.assertIsNotNone(complaint.verified_at)
        self.assertIsNotNone(complaint.resolved_at)
        history = list(complaint.updates.values_list("action", "from_status", "to_status", "note", "actor"))
        self.assertEqual(history[1:], [
            ("start_review", "submitted", "under_review", "", self.it_admin.pk),
            ("verify", "under_review", "verified", "", self.it_admin.pk),
            ("start_work", "verified", "in_progress", "Ordering a cable", self.it_admin.pk),
            ("resolve", "in_progress", "resolved", "Cable replaced", self.it_admin.pk),
        ])
        messages = list(
            Notification.objects.filter(recipient=self.reporter).order_by("pk").values_list("event", "message")
        )
        tid = complaint.tracking_id
        reopen_by = timezone.localdate(complaint.resolved_at) + timedelta(days=7)
        self.assertEqual(messages, [
            ("status_changed", f"{tid} is now Under review"),
            ("status_changed", f"{tid} is now Verified"),
            ("status_changed", f"{tid} is now In progress"),
            ("status_changed", f"{tid} was resolved. Please confirm or reopen by {reopen_by.day} {reopen_by:%b %Y}"),
        ])
        # The acting admin is never notified about their own action.
        self.assertFalse(Notification.objects.filter(recipient=self.it_admin).exclude(event="new_complaint").exists())

    def test_tc65_vr03_only_listed_transitions_are_allowed(self):
        for status in Complaint.Status.values:
            for action in ["start_review", "verify", "reject", "start_work", "resolve"]:
                with self.subTest(status=status, action=action):
                    complaint = self.at_status(status)
                    if status in Complaint.ALLOWED_FROM[action]:
                        self.run_action(complaint, action, self.it_admin)
                        self.assertNotEqual(Complaint.objects.get(pk=complaint.pk).status, status)
                    else:
                        with self.assertRaises(ValidationError):
                            self.run_action(complaint, action, self.it_admin)
                        self.assertEqual(Complaint.objects.get(pk=complaint.pk).status, status)
                        self.assertEqual(complaint.updates.count(), 1)  # only "submitted"

    def test_tc66_vr02_only_own_department_or_super_admin_can_act(self):
        complaint = self.submit()
        for outsider in [self.fac_admin, self.reporter, self.stranger]:
            with self.subTest(user=outsider.email):
                with self.assertRaises(ValidationError):
                    complaint.start_review(outsider)
                with self.assertRaises(ValidationError):
                    complaint.add_note(outsider, "Hello", is_internal=False)
        self.assertEqual(Complaint.objects.get(pk=complaint.pk).status, "submitted")
        complaint.start_review(self.boss)  # Super Admin: any department (C-13)
        self.assertEqual(complaint.status, "under_review")
        self.assertEqual(complaint.updates.last().actor, self.boss)

    def test_tc67_vr05_verify_needs_priority_and_future_due_date(self):
        complaint = self.at_status("under_review")
        today = timezone.localdate()
        for priority, due in [("urgent", self.tomorrow()), ("", self.tomorrow()), ("high", None),
                              ("high", today), ("high", today - timedelta(days=1))]:
            with self.subTest(priority=priority, due=due):
                with self.assertRaises(ValidationError):
                    complaint.verify(self.it_admin, priority, due)
        self.assertEqual(Complaint.objects.get(pk=complaint.pk).status, "under_review")
        complaint.verify(self.it_admin, "low", self.tomorrow())
        self.assertEqual(Complaint.objects.get(pk=complaint.pk).status, "verified")

    def test_tc68_vr04_reject_needs_reason_and_resolve_needs_note(self):
        complaint = self.at_status("under_review")
        for blank in ["", "   ", None]:
            with self.assertRaises(ValidationError):
                complaint.reject(self.it_admin, blank)
        complaint.reject(self.it_admin, "  Duplicate of UF-0001  ")
        update = complaint.updates.last()
        self.assertEqual((complaint.status, update.action, update.note), ("rejected", "reject", "Duplicate of UF-0001"))
        self.assertEqual(
            Notification.objects.get(recipient=self.reporter).message,
            f"{complaint.tracking_id} was rejected: Duplicate of UF-0001",
        )
        # A long reason is shortened with "…" so the message fits 255 characters (docs/03 §4).
        long_one = self.at_status("under_review")
        long_one.reject(self.it_admin, "Out of scope. " * 40)
        message = Notification.objects.get(complaint=long_one, recipient=self.reporter).message
        self.assertEqual(len(message), 255)
        self.assertTrue(message.startswith(f"{long_one.tracking_id} was rejected: Out of scope."))
        self.assertTrue(message.endswith("…"))
        self.assertEqual(long_one.updates.last().note, ("Out of scope. " * 40).strip())  # history keeps it all
        working = self.at_status("in_progress")
        with self.assertRaises(ValidationError):
            working.resolve(self.it_admin, " ")
        self.assertEqual(Complaint.objects.get(pk=working.pk).status, "in_progress")

    def test_tc69_c07_resolve_with_optional_proof_photo(self):
        # 5 evidence files at submission do not block a proof photo (docs/05 Attachment).
        complaint = self.submit(files=[upload(f"p{n}.png") for n in range(5)])
        Complaint.objects.filter(pk=complaint.pk).update(status="in_progress")
        complaint.refresh_from_db()
        for bad in [upload("report.pdf"), upload("photo.jpg", kind="pdf"), upload("clip.mp4")]:
            with self.subTest(file=bad.name):
                with self.assertRaises(ValidationError):
                    complaint.resolve(self.it_admin, "Fixed", proof_file=bad)
        self.assertEqual(Complaint.objects.get(pk=complaint.pk).status, "in_progress")
        complaint.resolve(self.it_admin, "Fixed", proof_file=upload("after.jpg"))
        proof = complaint.attachments.get(kind=Attachment.Kind.PROOF_OF_FIX)
        self.assertEqual(
            (proof.original_name, proof.mime_type, proof.uploaded_by), ("after.jpg", "image/jpeg", self.it_admin)
        )
        self.assertTrue(proof.file.name.startswith(f"complaints/{complaint.tracking_id}/"))

    def test_tc70_failed_resolve_keeps_status_and_leaves_no_file(self):
        complaint = self.at_status("in_progress")
        folder = os.path.join(self.media_root, "complaints", complaint.tracking_id)
        files_before = sorted(os.listdir(folder)) if os.path.isdir(folder) else []
        with mock.patch.object(Notification.objects, "bulk_create", side_effect=RuntimeError):
            with self.assertRaises(RuntimeError):
                complaint.resolve(self.it_admin, "Fixed", proof_file=upload("after.jpg"))
        complaint.refresh_from_db()
        self.assertEqual((complaint.status, complaint.resolved_at), ("in_progress", None))
        self.assertFalse(complaint.attachments.exists())
        self.assertEqual(complaint.updates.count(), 1)
        self.assertEqual(sorted(os.listdir(folder)) if os.path.isdir(folder) else [], files_before)

    def test_tc71_start_work_after_reopen_keeps_due_date(self):
        due = timezone.localdate() - timedelta(days=2)
        complaint = self.at_status("reopened", priority="medium", due_date=due)
        complaint.start_work(self.it_admin)
        complaint.refresh_from_db()
        self.assertEqual((complaint.status, complaint.due_date), ("in_progress", due))  # docs/03 §7
        self.assertTrue(complaint.is_overdue)
        self.assertEqual(complaint.updates.last().from_status, "reopened")

    def test_tc72_c10_withdraw_by_reporter_while_submitted_notifies_department(self):
        User.objects.create_user(  # a suspended IT admin is not notified
            "old.it@northsouth.edu", "pw", full_name="Old", role=User.Role.DEPT_ADMIN,
            department=self.it, account_state=User.AccountState.SUSPENDED,
        )
        complaint = self.submit()
        for not_reporter in [self.other, self.it_admin, self.boss]:
            with self.assertRaises(ValidationError):
                complaint.withdraw(not_reporter)
        complaint.withdraw(self.reporter)
        self.assertEqual(Complaint.objects.get(pk=complaint.pk).status, "withdrawn")
        self.assertEqual(complaint.updates.last().action, "withdraw")
        withdrawn = Notification.objects.filter(message=f"{complaint.tracking_id} was withdrawn by the student")
        self.assertEqual(list(withdrawn.values_list("recipient", flat=True)), [self.it_admin.pk])
        with self.assertRaises(ValidationError):  # only while Submitted
            self.at_status("under_review").withdraw(self.reporter)

    def test_tc73_add_note_public_or_internal_on_allowed_statuses(self):
        complaint = self.at_status("resolved")  # notes are allowed on Resolved
        complaint.add_note(self.it_admin, "Please confirm the fix.", is_internal=False)
        complaint.add_note(self.it_admin, "Vendor invoice pending.", is_internal=True)
        notes = list(complaint.updates.filter(action="note").values_list("note", "is_internal", "to_status"))
        self.assertEqual(notes, [
            ("Please confirm the fix.", False, "resolved"),
            ("Vendor invoice pending.", True, "resolved"),
        ])
        self.assertEqual(Notification.objects.filter(recipient=self.reporter, event="note_added").count(), 1)
        with self.assertRaises(ValidationError):
            complaint.add_note(self.it_admin, "  ", is_internal=False)
        for status in ["closed", "rejected", "withdrawn"]:
            with self.subTest(status=status):
                with self.assertRaises(ValidationError):
                    self.at_status(status).add_note(self.it_admin, "Late note", is_internal=False)

    def test_tc74_allowed_actions_and_hints(self):
        def bar(status, user=None):
            complaint = self.at_status(status)
            return {b["slug"]: (b["enabled"], b["hint"]) for b in complaint.allowed_actions(user or self.it_admin)}

        self.assertEqual(bar("submitted"), {
            "start_review": (True, ""),
            "verify": (False, "Available after Start review"),
            "reject": (False, "Available after Start review"),
            "start_work": (False, "Available after Verify"),
            "resolve": (False, "Available after Start work"),
        })
        self.assertEqual(bar("under_review")["verify"], (True, ""))
        self.assertEqual(bar("under_review")["reject"], (True, ""))
        self.assertEqual(bar("verified"), {
            "start_review": (False, "Done"),
            "verify": (False, "Done"),
            "reject": (False, "Not available: complaint is Verified"),
            "start_work": (True, ""),
            "resolve": (False, "Available after Start work"),
        })
        self.assertEqual(bar("reopened")["start_work"], (True, ""))
        self.assertEqual(bar("resolved")["resolve"], (False, "Done"))
        for final in ["rejected", "closed", "withdrawn"]:
            label = Complaint.Status(final).label
            self.assertEqual(set(bar(final).values()), {(False, f"Not available: complaint is {label}")})
        self.assertEqual(list(bar("submitted", self.boss)), ["start_review", "verify", "reject", "start_work", "resolve"])
        complaint = self.submit()
        self.assertEqual(complaint.allowed_actions(self.fac_admin), [])
        self.assertEqual(complaint.allowed_actions(self.reporter), [])
        self.assertTrue(complaint.can_add_note(self.it_admin))
        self.assertFalse(complaint.can_add_note(self.fac_admin))
        self.assertFalse(self.at_status("closed").can_add_note(self.boss))


# --- Sprint 3: pages (notifications, S-04 withdraw, console) -------------------


class NotificationPageTests(WorkflowFixtures):
    """C-11: S-05/A-06 list, mark all as read, bell count, S-01 latest (TC-75, TC-76)."""

    def test_tc75_list_bell_and_mark_all_read(self):
        complaint = self.submit()  # notifies the IT admin
        complaint.start_review(self.it_admin)  # notifies the reporter
        complaint.add_note(self.it_admin, "Checking the cable.", is_internal=False)
        self.submit(category=self.electrical, files=[upload("photo.jpg")])  # FAC: not for the IT admin

        self.client.force_login(self.reporter)
        response = self.client.get(reverse("notifications:list"))
        self.assertEqual([n.message for n in response.context["notifications"]],
                         [f"New note on {complaint.tracking_id}", f"{complaint.tracking_id} is now Under review"])
        detail_url = reverse("student:complaint_detail", args=[complaint.tracking_id])
        self.assertContains(response, f'href="{detail_url}"', count=2)
        self.assertContains(response, "notification-unread", count=2)
        self.assertContains(response, 'aria-label="Notifications, 2 unread"')  # bell, from the context processor
        self.assertEqual(Notification.objects.filter(recipient=self.reporter, is_read=False).count(), 2)  # opening reads nothing

        self.assertEqual(self.client.get(reverse("notifications:mark_all_read")).status_code, 405)
        response = self.client.post(reverse("notifications:mark_all_read"), follow=True)
        self.assertRedirects(response, reverse("notifications:list"))
        self.assertNotContains(response, "notification-unread")
        self.assertContains(response, 'aria-label="Notifications"')
        self.assertTrue(Notification.objects.filter(recipient=self.it_admin, is_read=False).exists())  # only own

        self.client.force_login(self.it_admin)
        response = self.client.get(reverse("notifications:list"))
        self.assertEqual(len(response.context["notifications"]), 1)  # own department only
        self.assertContains(response, reverse("console:complaint_detail", args=[complaint.tracking_id]))

    def test_tc76_student_home_shows_five_latest_notifications(self):
        complaint = self.submit()
        complaint.start_review(self.it_admin)
        for number in range(5):
            complaint.add_note(self.it_admin, f"Update {number}", is_internal=False)
        self.client.force_login(self.reporter)
        response = self.client.get(reverse("student:home"))
        latest = response.context["latest_notifications"]
        self.assertEqual(len(latest), 5)
        self.assertNotIn("is now Under review", [n.message for n in latest])  # the oldest is left out
        self.assertContains(response, reverse("notifications:list"))


class WithdrawPageTests(WorkflowFixtures):
    """C-10: Withdraw on S-04 (TC-77)."""

    def test_tc77_withdraw_button_and_post(self):
        complaint = self.submit()
        complaint.support(self.other)
        url = reverse("student:complaint_action", args=[complaint.tracking_id, "withdraw"])
        detail = reverse("student:complaint_detail", args=[complaint.tracking_id])

        self.client.force_login(self.other)  # supporter: limited view, no button, refused
        self.assertNotContains(self.client.get(detail), url)
        self.client.post(url)
        self.assertEqual(Complaint.objects.get(pk=complaint.pk).status, "submitted")
        self.client.force_login(self.stranger)
        self.assertEqual(self.client.post(url).status_code, 404)

        self.client.force_login(self.reporter)
        response = self.client.get(detail)
        self.assertContains(response, url)
        self.assertContains(response, "Withdraw this complaint? This cannot be undone.")
        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, detail)
        self.assertContains(response, f"{complaint.tracking_id} was withdrawn.")
        self.assertEqual(Complaint.objects.get(pk=complaint.pk).status, "withdrawn")
        self.assertNotContains(response, url)  # no button once withdrawn
        self.assertNotContains(self.client.get(reverse("student:complaint_detail", args=[
            self.at_status("under_review").tracking_id])), "Withdraw this complaint")


class QueuePageTests(WorkflowFixtures):
    """A-02 queue: scope, filters, search, sort, overdue flag (TC-78)."""

    def test_tc78_queue_scope_filters_search_and_sort(self):
        today = timezone.localdate()
        late = self.at_status("in_progress", priority="high", due_date=today - timedelta(days=1))
        soon = self.at_status("verified", priority="low", due_date=today + timedelta(days=2))
        new = self.submit()
        closed = self.at_status("closed")
        fac = self.submit(category=self.electrical, files=[upload("photo.jpg")], reporter=self.other)
        queue = reverse("console:queue")

        def ids(user, **params):
            self.client.force_login(user)
            return [c.tracking_id for c in self.client.get(queue, params).context["complaints"]]

        # Default: open complaints of the own department, soonest due first, no due date last.
        self.assertEqual(ids(self.it_admin), [late.tracking_id, soon.tracking_id, new.tracking_id])
        self.assertIn(closed.tracking_id, ids(self.it_admin, status="all"))
        self.assertEqual(ids(self.it_admin, status="closed"), [closed.tracking_id])
        self.assertEqual(ids(self.it_admin, priority="low"), [soon.tracking_id])
        self.assertEqual(ids(self.it_admin, overdue="1"), [late.tracking_id])
        self.assertEqual(ids(self.it_admin, category=self.network.pk), [])
        self.assertEqual(ids(self.it_admin, sort="updated")[0], new.tracking_id)
        self.assertEqual(ids(self.it_admin, q=fac.tracking_id), [])  # other department: nothing (VR-02)
        self.assertEqual(ids(self.it_admin, department=self.fac.pk), ids(self.it_admin))  # not for Dept Admins
        self.assertEqual(ids(self.fac_admin, q="Name other"), [fac.tracking_id])  # reporter name
        self.assertEqual(ids(self.fac_admin, q="OTHER@north"), [fac.tracking_id])  # email
        # Super Admin: every department, with a department filter.
        self.assertIn(fac.tracking_id, ids(self.boss))
        self.assertEqual(ids(self.boss, department=self.fac.pk), [fac.tracking_id])

        self.client.force_login(self.it_admin)
        response = self.client.get(queue)
        self.assertContains(response, 'class="row-overdue"', count=1)
        self.assertContains(response, reverse("console:complaint_detail", args=[late.tracking_id]))
        self.client.force_login(self.reporter)
        self.assertEqual(self.client.get(queue).status_code, 403)


class ConsoleDetailTests(WorkflowFixtures):
    """A-03: access, reporter card, history, action bar, actions, files (TC-79 to TC-82)."""

    def detail(self, complaint, user=None):
        self.client.force_login(user or self.it_admin)
        return self.client.get(reverse("console:complaint_detail", args=[complaint.tracking_id]))

    def act(self, complaint, action, data=None, user=None):
        self.client.force_login(user or self.it_admin)
        url = reverse("console:complaint_action", args=[complaint.tracking_id, action])
        return self.client.post(url, data or {})

    def test_tc79_access_reporter_card_and_history(self):
        self.reporter.gender = User.Gender.FEMALE
        self.reporter.save()
        complaint = self.submit()
        complaint.support(self.other)
        complaint.support(self.stranger)
        complaint.start_review(self.it_admin)
        complaint.add_note(self.it_admin, "Vendor called.", is_internal=True)
        self.assertEqual(self.detail(complaint, self.fac_admin).status_code, 404)  # VR-02
        self.assertEqual(self.detail(complaint, self.reporter).status_code, 403)
        self.assertEqual(self.detail(complaint, self.boss).status_code, 200)
        response = self.detail(complaint)
        self.assertContains(response, self.reporter.full_name)
        self.assertContains(response, "Complaints filed: 1 · Rejected: 0")
        self.assertContains(response, "img/avatars/neutral.svg")  # VR-16: never the reporter's own avatar
        self.assertNotContains(response, "female")
        self.assertContains(response, 'aria-disabled="true" title="Student records arrive in Sprint 4"')
        history = response.context["history"]
        self.assertEqual([h["action"] for h in history], ["Submitted", "Me too", "Review started", "Note"])
        self.assertEqual(history[1]["actors"], [self.other.full_name, self.stranger.full_name])  # grouped
        self.assertTrue(history[3]["is_internal"])
        self.assertContains(response, "Vendor called.")
        self.assertContains(response, self.it_admin.full_name)  # admin pages show names

    def test_tc80_action_bar_matches_allowed_actions(self):
        response = self.detail(self.submit())
        self.assertContains(response, "<details", count=1)  # only Add note: Start review needs no form
        self.assertContains(response, "Available after Start review", count=2)
        self.assertContains(response, "disabled>Verify</button>")
        complaint = self.at_status("under_review")
        response = self.detail(complaint)
        self.assertContains(response, '<summary class="btn btn-primary">Verify</summary>')
        self.assertContains(response, '<summary class="btn btn-danger">Reject</summary>')
        self.assertContains(response, "disabled>Start review</button>")
        response = self.detail(self.at_status("closed"))
        self.assertContains(response, "Not available: complaint is Closed", count=5)
        self.assertNotContains(response, "Add note")
        self.assertEqual(self.detail(complaint, self.boss).context["buttons"][1]["enabled"], True)

    def test_tc81_actions_post_redirect_or_show_errors(self):
        complaint = self.submit()
        detail = reverse("console:complaint_detail", args=[complaint.tracking_id])
        self.assertEqual(self.act(complaint, "start_review", user=self.fac_admin).status_code, 404)  # VR-02
        self.assertEqual(self.act(complaint, "reassign").status_code, 404)  # Sprint 4
        self.client.force_login(self.it_admin)
        self.assertEqual(self.client.get(reverse("console:complaint_action", args=[complaint.tracking_id, "start_review"])).status_code, 405)
        # VR-03: verify while Submitted is refused with the form open.
        response = self.act(complaint, "verify", {"priority": "high", "due_date": self.tomorrow().isoformat()})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context["open_action"], "verify")
        self.assertContains(response, "Verify is not possible while the complaint is Submitted.", status_code=400)

        self.assertRedirects(self.act(complaint, "start_review"), detail)
        response = self.act(complaint, "verify", {"priority": "high", "due_date": timezone.localdate().isoformat()})
        self.assertContains(response, "The due date must be later than today.", status_code=400)  # VR-05
        self.assertContains(response, "<details class=\"action-form\" open>", status_code=400)
        self.assertContains(self.act(complaint, "reject", {"reason": " "}), "This field is required.", status_code=400)  # VR-04
        self.assertRedirects(self.act(complaint, "verify", {"priority": "high", "due_date": self.tomorrow().isoformat()}), detail)
        self.assertRedirects(self.act(complaint, "start_work", {"note": ""}), detail)
        self.assertContains(self.act(complaint, "resolve", {"note": "Fixed", "proof_file": upload("x.pdf")}),
                            "must be a JPG, PNG or WEBP photo", status_code=400)
        response = self.client.post(
            reverse("console:complaint_action", args=[complaint.tracking_id, "resolve"]),
            {"note": "Fixed", "proof_file": upload("after.png")}, follow=True,
        )
        self.assertContains(response, f"{complaint.tracking_id} is now Resolved.")
        self.assertEqual(Complaint.objects.get(pk=complaint.pk).status, "resolved")
        self.assertContains(response, reverse("console:attachment", args=[complaint.tracking_id, complaint.attachments.get().pk]))
        self.assertRedirects(self.act(complaint, "note", {"note": "Internal check", "visibility": "internal"}), detail)
        self.assertTrue(complaint.updates.get(action="note").is_internal)

    def test_tc82_console_attachment_is_permission_checked(self):
        complaint = self.submit(files=[upload("photo.jpg")])
        url = reverse("console:attachment", args=[complaint.tracking_id, complaint.attachments.get().pk])
        for user, expected in [(self.it_admin, 200), (self.boss, 200), (self.fac_admin, 404), (self.reporter, 403)]:
            with self.subTest(user=user.email):
                self.client.force_login(user)
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected)
                if expected == 200:
                    self.assertEqual(b"".join(response.streaming_content), FILE_BYTES["jpg"])
                    self.assertEqual(response["Cache-Control"], "private")
