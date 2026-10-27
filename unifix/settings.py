"""
Django settings for the UniFix project.

Secrets and machine-specific values come from a `.env` file in the project
root (copy `.env.example` to `.env`). Names follow docs/05_data_dictionary.md.
"""

import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env into os.environ (values already set in the environment win).
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY is missing. Copy .env.example to .env.")

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = [h for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h]


# Applications

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # UniFix apps (docs/05 §2)
    "accounts",
    "complaints",
    "notifications",
    "console",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "unifix.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "notifications.context_processors.unread_count",  # bell count (C-11)
            ],
        },
    },
]

WSGI_APPLICATION = "unifix.wsgi.application"


# Database: SQLite in development (docs/07)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Accounts (docs/05 §3 accounts.User)

AUTH_USER_MODEL = "accounts.User"

# Lets suspended or deleted users reach LoginForm.confirm_login_allowed(),
# which shows "Account inactive" instead of a generic error (VR-11).
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.AllowAllUsersModelBackend"]

LOGIN_URL = "accounts:login"
LOGOUT_REDIRECT_URL = "accounts:login"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Tests only (`manage.py test`): a fast, insecure hasher so the suite runs quickly
# (I-33). Real passwords always use Django's default (PBKDF2) hasher.
if len(sys.argv) > 1 and sys.argv[1] == "test":
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


# Internationalization

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JS) and uploaded media

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Uploads are stored under MEDIA_ROOT but never served from a public URL: the
# student:attachment view sends each file after a permission check (NFR-03).
# There is deliberately no MEDIA_URL route in unifix/urls.py.
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# A request with more files than this is refused outright (HTTP 400). It is set
# above the 5-file limit (VR-07) so that 6 to 10 files get the form's friendly
# message instead.
DATA_UPLOAD_MAX_NUMBER_FILES = 10

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
