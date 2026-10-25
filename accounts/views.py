"""Login, logout, registration and profile views (P-01, P-02, S-06, A-07)."""

from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import User
from .permissions import signed_in_required


def role_home_url(user):
    """Where each role lands after logging in (P-01): students → S-01, admins → A-01."""
    if user.is_student():
        return reverse("student:home")
    return reverse("console:dashboard")


class UniFixLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True  # signed-in users skip the login page

    def get_default_redirect_url(self):
        # Used when there is no ?next= parameter.
        return role_home_url(self.request.user)


def register(request):
    """Student registration (C-01, VR-13). The new student is signed in straight away."""
    if request.user.is_authenticated:
        return redirect(role_home_url(request.user))

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to UniFix. Your account is ready.")
            return redirect(role_home_url(user))
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@signed_in_required
def profile(request):
    """S-06 / A-07 Profile: edit name and phone (C-15). Shared by all roles."""
    if request.method == "POST":
        # Edit a fresh copy: a ModelForm writes the posted values onto its instance
        # even when they are invalid, and request.user feeds the top bar (I-31).
        form = ProfileForm(request.POST, instance=User.objects.get(pk=request.user.pk))
        if form.is_valid():
            form.save()
            messages.success(request, "Profile saved.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(
        request,
        "accounts/profile.html",
        {"form": form, "password_form": PasswordChangeForm(request.user)},
    )


@signed_in_required
def password_change(request):
    """Change password (C-15). Posted from the profile page; errors show there."""
    if request.method != "POST":
        return redirect("accounts:profile")
    password_form = PasswordChangeForm(request.user, request.POST)
    if password_form.is_valid():
        user = password_form.save()
        update_session_auth_hash(request, user)  # stay signed in with the new password
        messages.success(request, "Password changed.")
        return redirect("accounts:profile")
    return render(
        request,
        "accounts/profile.html",
        {"form": ProfileForm(instance=request.user), "password_form": password_form},
    )
