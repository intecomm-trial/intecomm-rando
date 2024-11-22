import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "intecomm_rando"
base_dir = Path(__file__).resolve().parent.parent.parent


project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    SILENCED_SYSTEM_CHECKS=[
        "sites.E101",
    ],
    EDC_DX_LABELS=dict(hiv="HIV", dm="Diabetes", htn="Hypertension"),
    EDC_RANDOMIZATION_REGISTER_DEFAULT_RANDOMIZER=False,
    EDC_RANDOMIZATION_SKIP_VERIFY_CHECKS=True,
    EDC_RANDOMIZATION_LIST_PATH=base_dir / app_name / "tests" / "etc",
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
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
        "django_crypto_fields.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_adverse_event.apps.AppConfig",
        "adverse_event_app.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_dashboard.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "edc_lab_dashboard.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_review_dashboard.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_subject_dashboard.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "intecomm_rando.tests",
        "intecomm_rando.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
    add_lab_dashboard_middleware=True,
).settings

for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
