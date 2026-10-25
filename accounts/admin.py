"""Django admin setup for the custom User model.

Django's built-in UserAdmin expects a `username` field, so it is adjusted for
email login. `is_active`, `is_staff` and `is_superuser` are not edited here:
User.save() derives them from `account_state` and `role`.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .models import User


class UserAdminCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ["email", "full_name", "role", "department", "student_id"]


class UserAdminChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ["email", "full_name", "role", "department", "account_state"]
    list_filter = ["role", "account_state", "department"]
    search_fields = ["email", "full_name", "student_id"]
    ordering = ["email"]
    readonly_fields = ["is_active", "is_staff", "is_superuser", "last_login", "date_joined"]

    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Profile", {"fields": ["full_name", "student_id", "phone"]}),
        ("Role", {"fields": ["role", "department", "account_state"]}),
        ("Derived flags", {"fields": ["is_active", "is_staff", "is_superuser"]}),
        ("Dates", {"fields": ["last_login", "date_joined"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": [
                    "email", "full_name", "role", "department", "student_id",
                    "password1", "password2",
                ],
            },
        ),
    ]
