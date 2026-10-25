"""Login, logout and registration views (P-01, P-02)."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import LoginForm, RegisterForm


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
