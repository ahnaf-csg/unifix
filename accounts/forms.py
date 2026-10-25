"""Forms for login, registration and profile (P-01, P-02, S-06)."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm

from .models import NSU_EMAIL_DOMAIN, User

ACCOUNT_INACTIVE_MESSAGE = "Account inactive"

# Login type tabs on P-01 (docs/05 §3 "Login form field", VR-15).
LOGIN_TYPE_STUDENT = "student"
LOGIN_TYPE_STAFF = "staff"


class LoginForm(AuthenticationForm):
    """Email + password login (P-01). The `username` field holds the email."""

    login_type = forms.ChoiceField(
        choices=[(LOGIN_TYPE_STUDENT, "Student"), (LOGIN_TYPE_STAFF, "Staff")],
        initial=LOGIN_TYPE_STUDENT,
        widget=forms.RadioSelect,  # shown as tabs (templates/accounts/login.html)
    )
    field_order = ["login_type", "username", "password"]

    error_messages = {
        **AuthenticationForm.error_messages,
        "inactive": ACCOUNT_INACTIVE_MESSAGE,
        "use_staff_tab": "This is a staff account. Please use the Staff tab.",
        "use_student_tab": "This is a student account. Please use the Student tab.",
    }

    def clean_username(self):
        # Emails are stored in lower case, so compare in lower case.
        return self.cleaned_data["username"].strip().lower()

    def confirm_login_allowed(self, user):
        """Runs after the email and password are correct. Order matters."""
        # VR-11 first: suspended and deleted accounts cannot log in.
        if not user.is_active or user.account_state != User.AccountState.ACTIVE:
            raise forms.ValidationError(self.error_messages["inactive"], code="inactive")
        # VR-15: the chosen tab must match the role.
        login_type = self.cleaned_data.get("login_type")
        if user.is_student() and login_type != LOGIN_TYPE_STUDENT:
            raise forms.ValidationError(self.error_messages["use_student_tab"], code="wrong_tab")
        if not user.is_student() and login_type != LOGIN_TYPE_STAFF:
            raise forms.ValidationError(self.error_messages["use_staff_tab"], code="wrong_tab")


class RegisterForm(BaseUserCreationForm):
    """Student self-registration (P-02, C-01). Admins are created by the Super Admin."""

    class Meta:
        model = User
        fields = ["full_name", "student_id", "email", "phone"]
        labels = {"email": "NSU email", "student_id": "Student ID"}
        help_texts = {"email": f"Must end with {NSU_EMAIL_DOMAIN}"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student_id"].required = True
        self.fields["password2"].label = "Confirm password"

    def clean_email(self):
        # VR-13: an @northsouth.edu address that is not already registered.
        email = self.cleaned_data["email"].strip().lower()
        if not email.endswith(NSU_EMAIL_DOMAIN):
            raise forms.ValidationError(f"Use your {NSU_EMAIL_DOMAIN} email address.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT  # registration is for students only
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Edit own name and phone (C-15). Email, role and student ID are read-only."""

    class Meta:
        model = User
        fields = ["full_name", "phone"]
