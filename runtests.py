#!/usr/bin/env python
import logging
import os.path
from pathlib import Path

from edc_constants.constants import IGNORE
from edc_test_utils import DefaultTestSettings, func_main

app_name = "intecomm_rando"
base_dir = Path(__file__).resolve().parent


project_settings = DefaultTestSettings(
    calling_file=__file__,
    EDC_NAVBAR_VERIFY_ON_LOAD=IGNORE,
    EDC_AUTH_CODENAMES_WARN_ONLY=True,
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    add_dashboard_middleware=True,
    add_lab_dashboard_middleware=True,
    EDC_DX_LABELS=dict(hiv="HIV", dm="Diabetes", htn="Hypertension"),
    EDC_RANDOMIZATION_REGISTER_DEFAULT_RANDOMIZER=False,
    EDC_RANDOMIZATION_SKIP_VERIFY_CHECKS=True,
    EDC_RANDOMIZATION_LIST_PATH=os.path.join(base_dir, app_name, "tests", "etc"),
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
        "edc_appointment.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        # "intecomm_consent.apps.AppConfig",
        "intecomm_rando.tests",
        "intecomm_rando.apps.AppConfig",
    ],
).settings


def main():
    func_main(project_settings, f"{app_name}.tests")


if __name__ == "__main__":
    logging.basicConfig()
    main()
