"""Complaint models (docs/05 §3).

Department and Category came in Sprint 1 and are managed in the Django admin
panel (C-16). Sprint 2 adds Complaint, Attachment, ComplaintUpdate and Support.
Rating follows in Sprint 4.

Workflow logic lives in Complaint methods (CLAUDE.md): each one checks the
rules, writes a ComplaintUpdate (history) and the notifications, inside one
database transaction. Views only call these methods.
"""

import os
import uuid
from datetime import timedelta

import filetype
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from accounts.models import User
from notifications.models import Notification


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


# --- File rules (VR-07) ----------------------------------------------------

# Allowed extension → file types the content may have. The type is detected
# from the first bytes of the file (filetype library), never from the name or
# from what the browser claims.
ALLOWED_FILE_TYPES = {
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".png": {"image/png"},
    ".webp": {"image/webp"},
    ".mp4": {"video/mp4", "video/x-m4v"},
    ".mov": {"video/quicktime"},
    ".pdf": {"application/pdf"},
}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB per file
MAX_FILES = 5  # per complaint


def check_attachment_file(uploaded_file):
    """Check one uploaded file against VR-07 and return its detected file type.

    Raises ValidationError with a message naming the file.
    """
    name = os.path.basename(uploaded_file.name)
    extension = os.path.splitext(name)[1].lower()
    if extension not in ALLOWED_FILE_TYPES:
        raise ValidationError(f"{name}: only JPG, PNG, WEBP, MP4, MOV and PDF files are allowed.")
    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValidationError(f"{name}: files can be at most 15 MB.")
    uploaded_file.seek(0)
    kind = filetype.guess(uploaded_file.read(8192))  # the signature is in the first bytes
    uploaded_file.seek(0)
    if kind is None or kind.mime not in ALLOWED_FILE_TYPES[extension]:
        raise ValidationError(f"{name}: the file content does not match its {extension} extension.")
    return kind.mime


def attachment_upload_to(attachment, filename):
    """media/complaints/<tracking_id>/<random>.<ext>: the user's file name never reaches the disk."""
    extension = os.path.splitext(filename)[1].lower()
    return f"complaints/{attachment.complaint.tracking_id}/{uuid.uuid4().hex}{extension}"


def normalise_room(room):
    """'L 3' and 'l3' are the same room for the duplicate rule (docs/03 §6)."""
    return "".join((room or "").split()).lower()


# --- Complaint -------------------------------------------------------------


class Complaint(models.Model):
    class Status(models.TextChoices):  # docs/03 §1
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under review"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"
        IN_PROGRESS = "in_progress", "In progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"
        REOPENED = "reopened", "Reopened"
        WITHDRAWN = "withdrawn", "Withdrawn"

    OPEN_STATUSES = [
        Status.SUBMITTED,
        Status.UNDER_REVIEW,
        Status.VERIFIED,
        Status.IN_PROGRESS,
        Status.REOPENED,
    ]

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Building(models.TextChoices):
        NAC = "nac", "NAC"
        SAC = "sac", "SAC"
        LIBRARY = "library", "Library"
        ADMIN_BUILDING = "admin_building", "Admin Building"
        PLAZA = "plaza", "Plaza"
        OTHER = "other", "Other"

    # NULL until the first insert gives the row its primary key (see save()).
    tracking_id = models.CharField(max_length=12, unique=True, null=True, blank=True, editable=False)
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="complaints"
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="complaints")
    # Copied from the category at submission (C-04); changed only by reassign.
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="complaints")
    title = models.CharField(max_length=120)
    description = models.TextField()
    building = models.CharField(max_length=20, choices=Building.choices)
    room = models.CharField(max_length=30, blank=True)  # label only, e.g. 512 or L3
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    priority = models.CharField(max_length=10, choices=Priority.choices, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)  # reserved for OP-01
    reopen_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tracking_id} {self.title}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            if not self.tracking_id:
                # The primary key exists only after the insert: UF-0001, UF-0002, ...
                self.tracking_id = f"UF-{self.pk:04d}"
                super().save(update_fields=["tracking_id"])

    # --- Computed values (docs/03 §5) --------------------------------------

    @property
    def is_overdue(self):
        return (
            self.due_date is not None
            and self.due_date < timezone.localdate()
            and self.status in [self.Status.VERIFIED, self.Status.IN_PROGRESS, self.Status.REOPENED]
        )

    @property
    def can_reopen(self):
        return (
            self.status == self.Status.RESOLVED
            and self.resolved_at is not None
            and timezone.localdate() <= timezone.localdate(self.resolved_at) + timedelta(days=7)
        )

    @property
    def support_count(self):
        return self.supports.count()

    @property
    def affected_count(self):
        return self.support_count + 1  # supporters + the reporter

    @property
    def location(self):
        """Building label + room, e.g. "NAC 512" (docs/05 §3)."""
        return f"{self.get_building_display()} {self.room}".strip()

    @property
    def status_badge_class(self):
        """CSS class for partials/status_badge.html: under_review → badge-under-review."""
        return "badge-" + self.status.replace("_", "-")

    @property
    def is_open(self):
        return self.status in self.OPEN_STATUSES

    # --- Submission and duplicates (C-02, C-03, C-04) ----------------------

    @classmethod
    def find_duplicates(cls, category, building, room):
        """Open complaints with the same category, building and room (docs/03 §6).

        Rooms are compared without case or spaces; if either room is blank,
        the building alone decides.
        """
        room_key = normalise_room(room)
        candidates = cls.objects.filter(
            category=category, building=building, status__in=cls.OPEN_STATUSES
        ).select_related("category", "department")
        return [
            complaint
            for complaint in candidates
            if not room_key or not normalise_room(complaint.room) or normalise_room(complaint.room) == room_key
        ]

    @classmethod
    def submit(cls, reporter, category, building, room, title, description, files=()):
        """Create a complaint with its files, history and notifications (docs/03 §4 Submit)."""
        files = list(files)
        if not reporter.is_student():
            raise ValidationError("Only students can submit complaints.")
        if not (category.is_active and category.department.is_active):
            raise ValidationError("This category is no longer available.")
        if category.requires_attachment and not files:
            raise ValidationError("This category needs at least one photo, video or PDF.")  # VR-08
        if len(files) > MAX_FILES:
            raise ValidationError(f"You can attach at most {MAX_FILES} files.")  # VR-07
        checked_files = [(f, check_attachment_file(f)) for f in files]  # VR-07

        with transaction.atomic():
            complaint = cls.objects.create(
                reporter=reporter,
                category=category,
                department=category.department,  # routing (C-04)
                building=building,
                room=room.strip(),
                title=title,
                description=description,
            )
            for uploaded_file, mime_type in checked_files:
                Attachment.objects.create(
                    complaint=complaint,
                    file=uploaded_file,
                    kind=Attachment.Kind.EVIDENCE,
                    original_name=os.path.basename(uploaded_file.name)[:255],
                    mime_type=mime_type,
                    size_bytes=uploaded_file.size,
                    uploaded_by=reporter,
                )
            complaint.updates.create(
                actor=reporter,
                action=ComplaintUpdate.Action.SUBMITTED,
                to_status=cls.Status.SUBMITTED,
            )
            admins = User.objects.filter(
                role=User.Role.DEPT_ADMIN, department=complaint.department, is_active=True
            )
            Notification.objects.bulk_create(
                Notification(
                    recipient=admin,
                    complaint=complaint,
                    event=Notification.Event.NEW_COMPLAINT,
                    message=f"New complaint {complaint.tracking_id}: {title}"[:255],
                )
                for admin in admins
            )
        return complaint

    def support(self, student):
        """"Me too": the student is affected by this complaint too (C-03, VR-09)."""
        if not student.is_student():
            raise ValidationError("Only students can support complaints.")
        if student.pk == self.reporter_id:
            raise ValidationError("You cannot support your own complaint.")
        if not self.is_open:
            raise ValidationError("Only open complaints can be supported.")
        with transaction.atomic():
            if self.supports.filter(student=student).exists():
                raise ValidationError("You already support this complaint.")
            Support.objects.create(complaint=self, student=student)
            self.updates.create(
                actor=student,
                action=ComplaintUpdate.Action.SUPPORT,
                from_status=self.status,
                to_status=self.status,
            )
            self.save(update_fields=["updated_at"])


class Attachment(models.Model):
    """Evidence from the student or a proof-of-fix photo from an admin (Sprint 3)."""

    class Kind(models.TextChoices):
        EVIDENCE = "evidence", "Evidence"
        PROOF_OF_FIX = "proof_of_fix", "Proof of fix"

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=attachment_upload_to, max_length=255)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.EVIDENCE)
    original_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100)
    size_bytes = models.PositiveIntegerField()
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at", "pk"]

    def __str__(self):
        return self.original_name

    @property
    def is_image(self):
        return self.mime_type.startswith("image/")


class ComplaintUpdate(models.Model):
    """One history entry per action (C-08)."""

    class Action(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        SUPPORT = "support", "Me too"
        START_REVIEW = "start_review", "Review started"
        VERIFY = "verify", "Verified"
        REJECT = "reject", "Rejected"
        START_WORK = "start_work", "Work started"
        RESOLVE = "resolve", "Marked resolved"
        CLOSE = "close", "Fix confirmed"
        REOPEN = "reopen", "Reopened"
        WITHDRAW = "withdraw", "Withdrawn"
        REASSIGN = "reassign", "Reassigned"
        NOTE = "note", "Note"

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="updates")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    action = models.CharField(max_length=20, choices=Action.choices)
    from_status = models.CharField(max_length=20, choices=Complaint.Status.choices, blank=True)
    to_status = models.CharField(max_length=20, choices=Complaint.Status.choices, blank=True)
    from_department = models.ForeignKey(
        Department, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    to_department = models.ForeignKey(
        Department, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    note = models.TextField(blank=True)
    is_internal = models.BooleanField(default=False)  # hidden from students
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]

    def __str__(self):
        return f"{self.complaint.tracking_id}: {self.get_action_display()}"


class Support(models.Model):
    """A "Me too" from a student who is affected by someone else's complaint."""

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="supports")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="supports")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            # VR-09 backstop: the database itself refuses a second "Me too".
            models.UniqueConstraint(fields=["complaint", "student"], name="unique_support"),
        ]

    def __str__(self):
        return f"{self.student} supports {self.complaint.tracking_id}"
