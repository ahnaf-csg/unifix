"""Custom user model (docs/05 §3 accounts.User).

Users log in with their email address. One `role` field separates students,
department admins and the super admin. Accounts are never hard-deleted:
`account_state` records suspended and deleted accounts, and `is_active` is kept
in sync so Django blocks them from logging in (VR-11).
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models

NSU_EMAIL_DOMAIN = "@northsouth.edu"


class UserManager(BaseUserManager):
    """Creates users by email, because the model has no `username` field."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Used by `manage.py createsuperuser`; a superuser is always a Super Admin.
        extra_fields["role"] = User.Role.SUPER_ADMIN
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        DEPT_ADMIN = "dept_admin", "Department admin"
        SUPER_ADMIN = "super_admin", "Super admin"

    class AccountState(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        DELETED = "deleted", "Deleted"

    # Remove the inherited name fields; full_name replaces them (docs/05 §3).
    username = None
    first_name = None
    last_name = None

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=120)
    # NULL (not "") when empty, so many non-students can share "no student ID".
    student_id = models.CharField(max_length=20, null=True, blank=True, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    department = models.ForeignKey(
        "complaints.Department",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="admins",
    )
    account_state = models.CharField(
        max_length=20, choices=AccountState.choices, default=AccountState.ACTIVE
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    # --- Role checks -----------------------------------------------------

    def is_student(self):
        return self.role == self.Role.STUDENT

    def is_dept_admin(self):
        return self.role == self.Role.DEPT_ADMIN

    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN

    def can_view_complaint(self, complaint):
        """Who may open a complaint at all (VR-01, VR-02).

        Students: their own complaints (full view) and ones they support
        (limited view; the view decides which). Dept Admins: their department.
        """
        if self.is_super_admin():
            return True
        if self.is_dept_admin():
            return complaint.department_id == self.department_id
        return complaint.reporter_id == self.pk or complaint.supports.filter(student=self).exists()

    # --- Validation and saving -------------------------------------------

    def clean(self):
        """Role rules from docs/05 §3, checked by forms and the Django admin."""
        super().clean()
        self.email = (self.email or "").strip().lower()
        if self.is_student() and not self.email.endswith(NSU_EMAIL_DOMAIN):
            raise ValidationError({"email": f"Students must use an {NSU_EMAIL_DOMAIN} email address."})
        if self.is_dept_admin() and not self.department_id:
            raise ValidationError({"department": "A department admin needs a department."})
        if not self.is_dept_admin() and self.department_id:
            raise ValidationError({"department": "Only department admins have a department."})
        if not self.is_student() and self.student_id:
            raise ValidationError({"student_id": "Only students have a student ID."})

    def save(self, *args, **kwargs):
        self.email = (self.email or "").strip().lower()
        self.student_id = self.student_id or None  # store NULL, never ""
        # Derived flags, so they can never disagree with role and account_state:
        self.is_active = self.account_state == self.AccountState.ACTIVE  # VR-11
        self.is_staff = self.is_superuser = self.is_super_admin()  # Django admin (C-16)
        super().save(*args, **kwargs)

    # --- Account state (C-12, used by the Super Admin from Sprint 4) -----

    def suspend(self):
        self.account_state = self.AccountState.SUSPENDED
        self.save()

    def reactivate(self):
        self.account_state = self.AccountState.ACTIVE
        self.save()

    def soft_delete(self):
        # Keeps the row so complaint history stays intact (docs/07).
        self.account_state = self.AccountState.DELETED
        self.save()
