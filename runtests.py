#!/usr/bin/env python
import logging
import os.path
import sys
from pathlib import Path

import django
from django.conf import settings
from django.test.runner import DiscoverRunner

app_name = "intecomm_rando"
base_dir = Path(__file__).resolve().parent.parent

DEFAULT_SETTINGS = dict(  # nosec B106
    BASE_DIR=Path(__file__).resolve().parent.parent,
    SECRET_KEY="django-insecure",  # nosec B106
    DEBUG=True,
    SUBJECT_CONSENT_MODEL=None,
    SUBJECT_SCREENING_MODEL=None,
    ALLOWED_HOSTS=[],
    APP_NAME=app_name,
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.sites",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django_audit_fields.apps.AppConfig",
        "django_revision.apps.AppConfig",
        "edc_model.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "intecomm_rando.apps.AppConfig",
    ],
    MIDDLEWARE=[
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "edc_dashboard.middleware.DashboardMiddleware",
    ],
    ROOT_URLCONF="intecomm_rando.urls",
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ],
    WSGI_APPLICATION="intecomm_rando.wsgi.application",
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(base_dir, "db.sqlite3"),
        }
    },
    AUTH_PASSWORD_VALIDATORS=[
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ],
    LANGUAGE_CODE="en-us",
    TIME_ZONE="UTC",
    USE_I18N=True,
    USE_L10N=True,
    USE_TZ=True,
    STATIC_URL="/static/",
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)


def main():
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)
    django.setup()
    tags = [t.split("=")[1] for t in sys.argv if t.startswith("--tag")]
    failfast = True if [t for t in sys.argv if t == "--failfast"] else False
    failures = DiscoverRunner(failfast=failfast, tags=tags).run_tests([])
    sys.exit(bool(failures))


if __name__ == "__main__":
    logging.basicConfig()
    main()
