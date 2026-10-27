"""Complaint models (docs/05 §3).

Department and Category came in Sprint 1 and are managed in the Django admin
panel (C-16). Sprint 2 adds Complaint, Attachment, ComplaintUpdate and Support.
Sprint 3 adds the admin workflow methods and withdraw. Rating follows in Sprint 4.

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


# Proof of fix (C-07) is one photo: images only, otherwise the same checks as VR-07.
PROOF_FILE_TYPES = {".jpg", ".jpeg", ".png", ".webp"}


def check_proof_file(uploaded_file):
    """Check a proof-of-fix photo and return its detected file type."""
    name = os.path.basename(uploaded_file.name)
    if os.path.splitext(name)[1].lower() not in PROOF_FILE_TYPES:
        raise ValidationError(f"{name}: the proof of fix must be a JPG, PNG or WEBP photo.")
    return check_attachment_file(uploaded_file)


def attachment_upload_to(attachment, filename):
    """media/complaints/<tracking_id>/<random>.<ext>: the user's file name never reaches the disk."""
    extension = os.path.splitext(filename)[1].lower()
    return f"complaints/{attachment.complaint.tracking_id}/{uuid.uuid4().hex}{extension}"


def fit_message(start, text, limit=255):
    """start + text, with text shortened with "…" so the whole fits Notification.message."""
    text = " ".join(text.split())  # one line
    if len(start) + len(text) > limit:
        text = text[: limit - len(start) - 1].rstrip() + "…"
    return start + text


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

    # Statuses each action may start from (docs/03 §2, VR-03).
    ALLOWED_FROM = {
        "start_review": [Status.SUBMITTED],
        "verify": [Status.UNDER_REVIEW],
        "reject": [Status.UNDER_REVIEW],
        "start_work": [Status.VERIFIED, Status.REOPENED],
        "resolve": [Status.IN_PROGRESS],
        "withdraw": [Status.SUBMITTED],
    }
    # Add note: open statuses and Resolved (docs/03 §2).
    NOTE_STATUSES = OPEN_STATUSES + [Status.RESOLVED]

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
        # Every file is checked before anything is written (VR-07).
        checked_files = [(f, check_attachment_file(f)) for f in files]

        # A database rollback does not delete files already written to disk,
        # so on any error the stored files are removed before re-raising.
        stored_files = []
        try:
            return cls._create_submitted(
                reporter, category, building, room, title, description, checked_files, stored_files
            )
        except Exception:
            for stored in stored_files:
                stored.storage.delete(stored.name)
            raise

    @classmethod
    def _create_submitted(cls, reporter, category, building, room, title, description, checked_files, stored_files):
        """The database part of submit(); `stored_files` collects every file written."""
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
                attachment = Attachment(
                    complaint=complaint,
                    kind=Attachment.Kind.EVIDENCE,
                    original_name=os.path.basename(uploaded_file.name)[:255],
                    mime_type=mime_type,
                    size_bytes=uploaded_file.size,
                    uploaded_by=reporter,
                )
                attachment.file.save(uploaded_file.name, uploaded_file, save=False)  # writes to disk
                stored_files.append(attachment.file)
                attachment.save()
            complaint.updates.create(
                actor=reporter,
                action=ComplaintUpdate.Action.SUBMITTED,
                to_status=cls.Status.SUBMITTED,
            )
            complaint._notify(
                complaint.department_admins(),
                Notification.Event.NEW_COMPLAINT,
                f"New complaint {complaint.tracking_id}: {title}",
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

    # --- Workflow actions (docs/03 §2 and §4, Sprint 3) ---------------------
    #
    # Each method checks who is acting (VR-02) and whether the transition is
    # allowed (VR-03), then changes the complaint, writes one ComplaintUpdate
    # and the notifications, all in one transaction.

    def start_review(self, actor):
        with transaction.atomic():
            self._check_action(actor, "start_review")
            self.status = self.Status.UNDER_REVIEW
            self.save(update_fields=["status", "updated_at"])
            self._record(actor, ComplaintUpdate.Action.START_REVIEW, self.Status.SUBMITTED)

    def verify(self, actor, priority, due_date):
        """Valid complaint: set priority and due date (C-06, VR-05)."""
        if priority not in self.Priority.values:
            raise ValidationError("Choose a priority: low, medium or high.")
        if due_date is None or due_date <= timezone.localdate():
            raise ValidationError("The due date must be later than today.")
        with transaction.atomic():
            self._check_action(actor, "verify")
            self.status = self.Status.VERIFIED
            self.priority = priority
            self.due_date = due_date
            self.verified_at = timezone.now()
            self.save(update_fields=["status", "priority", "due_date", "verified_at", "updated_at"])
            self._record(actor, ComplaintUpdate.Action.VERIFY, self.Status.UNDER_REVIEW)

    def reject(self, actor, reason):
        """Invalid, duplicate or out of scope (final). A reason is required (VR-04)."""
        reason = (reason or "").strip()
        if not reason:
            raise ValidationError("Give a reason for rejecting the complaint.")
        with transaction.atomic():
            self._check_action(actor, "reject")
            self.status = self.Status.REJECTED
            self.save(update_fields=["status", "updated_at"])
            self._record(actor, ComplaintUpdate.Action.REJECT, self.Status.UNDER_REVIEW, note=reason)

    def start_work(self, actor, note=""):
        """From Verified, or from Reopened when work restarts (docs/03 §2)."""
        with transaction.atomic():
            self._check_action(actor, "start_work")
            from_status = self.status
            self.status = self.Status.IN_PROGRESS
            self.save(update_fields=["status", "updated_at"])
            self._record(actor, ComplaintUpdate.Action.START_WORK, from_status, note=(note or "").strip())

    def resolve(self, actor, note, proof_file=None):
        """Fixed: a note is required (VR-04); one proof photo is optional (C-07)."""
        note = (note or "").strip()
        if not note:
            raise ValidationError("Describe what was done to resolve the complaint.")
        mime_type = check_proof_file(proof_file) if proof_file else None
        # As in submit(): a rollback does not delete a file already written to disk.
        stored_files = []
        try:
            with transaction.atomic():
                self._check_action(actor, "resolve")
                self.status = self.Status.RESOLVED
                self.resolved_at = timezone.now()
                self.save(update_fields=["status", "resolved_at", "updated_at"])
                if proof_file:
                    attachment = Attachment(
                        complaint=self,
                        kind=Attachment.Kind.PROOF_OF_FIX,
                        original_name=os.path.basename(proof_file.name)[:255],
                        mime_type=mime_type,
                        size_bytes=proof_file.size,
                        uploaded_by=actor,
                    )
                    attachment.file.save(proof_file.name, proof_file, save=False)  # writes to disk
                    stored_files.append(attachment.file)
                    attachment.save()
                self._record(actor, ComplaintUpdate.Action.RESOLVE, self.Status.IN_PROGRESS, note=note)
        except Exception:
            for stored in stored_files:
                stored.storage.delete(stored.name)
            raise

    def withdraw(self, student):
        """The reporter cancels a complaint that is still Submitted (C-10)."""
        if student.pk != self.reporter_id:
            raise ValidationError("Only the student who reported this complaint can withdraw it.")
        with transaction.atomic():
            self._lock_and_check("withdraw")
            self.status = self.Status.WITHDRAWN
            self.save(update_fields=["status", "updated_at"])
            self._record(student, ComplaintUpdate.Action.WITHDRAW, self.Status.SUBMITTED)

    def add_note(self, actor, note, is_internal):
        """Public note (the reporter sees it) or internal note (admins only), C-08."""
        note = (note or "").strip()
        if not note:
            raise ValidationError("Write the note first.")
        with transaction.atomic():
            if not actor.can_act_on_complaint(self):  # VR-02
                raise ValidationError("You cannot act on this complaint.")
            self._lock_status()
            if self.status not in self.NOTE_STATUSES:
                raise ValidationError(f"Notes cannot be added to a {self.get_status_display().lower()} complaint.")
            self.save(update_fields=["updated_at"])
            self._record(actor, ComplaintUpdate.Action.NOTE, self.status, note=note, is_internal=bool(is_internal))

    # --- Helpers for the actions -------------------------------------------

    def _lock_status(self):
        """Re-read the status inside the transaction and lock the row, so two
        admins pressing buttons at the same moment cannot both act on an old status."""
        self.status = Complaint.objects.select_for_update().values_list("status", flat=True).get(pk=self.pk)

    def _lock_and_check(self, action):
        self._lock_status()
        if self.status not in self.ALLOWED_FROM[action]:  # VR-03
            label = dict(ADMIN_ACTIONS).get(action, "Withdraw")
            raise ValidationError(f"{label} is not possible while the complaint is {self.get_status_display()}.")

    def _check_action(self, actor, action):
        if not actor.can_act_on_complaint(self):  # VR-02
            raise ValidationError("You cannot act on this complaint.")
        self._lock_and_check(action)

    def _record(self, actor, action, from_status, note="", is_internal=False):
        """Write the history row and the notifications for one action (docs/03 §4)."""
        self.updates.create(
            actor=actor,
            action=action,
            from_status=from_status,
            to_status=self.status,
            note=note,
            is_internal=is_internal,
        )
        tracking_id = self.tracking_id
        if action == ComplaintUpdate.Action.NOTE:
            if not is_internal:  # internal notes notify nobody
                self._notify([self.reporter], Notification.Event.NOTE_ADDED, f"New note on {tracking_id}")
        elif action == ComplaintUpdate.Action.WITHDRAW:
            self._notify(self.department_admins(), Notification.Event.STATUS_CHANGED,
                         f"{tracking_id} was withdrawn by the student")
        elif action == ComplaintUpdate.Action.REJECT:
            self._notify([self.reporter], Notification.Event.STATUS_CHANGED,
                         fit_message(f"{tracking_id} was rejected: ", note))
        elif action == ComplaintUpdate.Action.RESOLVE:
            reopen_by = timezone.localdate(self.resolved_at) + timedelta(days=7)  # same window as can_reopen
            self._notify([self.reporter], Notification.Event.STATUS_CHANGED,
                         f"{tracking_id} was resolved. Please confirm or reopen by {reopen_by.day} {reopen_by:%b %Y}")
        else:
            self._notify([self.reporter], Notification.Event.STATUS_CHANGED,
                         f"{tracking_id} is now {self.get_status_display()}")

    def _notify(self, recipients, event, message):
        Notification.objects.bulk_create(
            Notification(recipient=recipient, complaint=self, event=event, message=message[:255])
            for recipient in recipients
        )

    def department_admins(self):
        """Active Dept Admins of this complaint's department (notification recipients)."""
        return User.objects.filter(role=User.Role.DEPT_ADMIN, department_id=self.department_id, is_active=True)

    # --- Buttons for the admin page (A-03) ----------------------------------

    def allowed_actions(self, user):
        """The five C-05 buttons, each {slug, label, enabled, hint} (docs/05 §3).

        Empty for users who cannot act on this complaint.
        """
        if not user.can_act_on_complaint(self):
            return []
        buttons = []
        for slug, label in ADMIN_ACTIONS:
            enabled = self.status in self.ALLOWED_FROM[slug]
            hint = "" if enabled else self._disabled_hint(slug)
            buttons.append({"slug": slug, "label": label, "enabled": enabled, "hint": hint})
        return buttons

    def _disabled_hint(self, slug):
        """"Done", "Available after <step>" or "Not available: complaint is <status>"."""
        here = STATUS_STEP.get(self.status)
        not_available = f"Not available: complaint is {self.get_status_display()}"
        if here is None:  # Rejected, Closed, Withdrawn
            return not_available
        if here < ACTION_STEP[slug]:
            return f"Available after {dict(ADMIN_ACTIONS)[PREVIOUS_ACTION[slug]]}"
        if slug == "reject":  # the complaint was verified instead
            return not_available
        return "Done"

    def can_add_note(self, user):
        return user.can_act_on_complaint(self) and self.status in self.NOTE_STATUSES


# The A-03 action bar, in order (C-05; slugs from the docs/05 action mapping).
ADMIN_ACTIONS = [
    ("start_review", "Start review"),
    ("verify", "Verify"),
    ("reject", "Reject"),
    ("start_work", "Start work"),
    ("resolve", "Mark resolved"),
]
# Position of each status along the main path, for the disabled-button hints.
# Reopened sits with Verified: work has to start again.
STATUS_STEP = {
    Complaint.Status.SUBMITTED: 0,
    Complaint.Status.UNDER_REVIEW: 1,
    Complaint.Status.VERIFIED: 2,
    Complaint.Status.REOPENED: 2,
    Complaint.Status.IN_PROGRESS: 3,
    Complaint.Status.RESOLVED: 4,
}
# The step at which each button becomes possible, and the button before it.
ACTION_STEP = {"start_review": 0, "verify": 1, "reject": 1, "start_work": 2, "resolve": 3}
PREVIOUS_ACTION = {"verify": "start_review", "reject": "start_review", "start_work": "verify", "resolve": "start_work"}


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
