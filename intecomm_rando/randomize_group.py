from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Tuple

from django.apps import apps as django_apps
from edc_constants.constants import COMPLETE, YES
from edc_randomization.constants import RANDOMIZED
from edc_randomization.site_randomizers import site_randomizers
from edc_randomization.utils import get_object_for_subject
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from intecomm_form_validators import IN_FOLLOWUP

from .exceptions import GroupAlreadyRandomized, GroupRandomizationError
from .group_eligibility import assess_group_eligibility
from .group_identifier import GroupIdentifier

if TYPE_CHECKING:
    from .models import RandomizationList

if TYPE_CHECKING:
    from intecomm_screening.models import PatientGroup, PatientLog


class RandomizeGroup:
    min_group_size = 14
    subject_consent_model = "intecomm_consent.subjectconsent"

    def __init__(self, instance: PatientGroup):
        self.instance = instance

    def randomize_group(self) -> Tuple[bool, datetime, str, str]:
        if self.instance.randomized:
            raise GroupAlreadyRandomized(f"Group is already randomized. Got {self.instance}.")
        if (
            self.instance.randomize_now != YES
            or self.instance.confirm_randomize_now != "RANDOMIZE"
        ):
            raise GroupRandomizationError(
                "Invalid. Expected YES. See `randomize_now`. "
                f"Got {self.instance.randomize_now}."
            )

        if self.instance.status != COMPLETE:
            raise GroupRandomizationError(f"Group is not complete. Got {self.instance}.")

        assess_group_eligibility(self.instance, called_by_rando=True)

        self.randomize()

        return True, get_utcnow(), self.instance.user_modified, self.instance.group_identifier

    def randomize(self) -> None:
        identifier_instance = GroupIdentifier(
            identifier_type="patient_group",
            group_identifier_as_pk=self.instance.group_identifier_as_pk,
            requesting_model=self.instance._meta.label_lower,
            site=self.instance.site,
        )
        report_datetime = get_utcnow()
        site_randomizers.randomize(
            "default",
            identifier=identifier_instance.identifier,
            report_datetime=report_datetime,
            site=self.instance.site,
            user=self.instance.user_created,
        )
        self.instance.group_identifier = identifier_instance.identifier
        self.instance.randomized = True
        self.instance.randomized_datetime = report_datetime
        self.instance.modified = report_datetime
        self.instance.status = IN_FOLLOWUP
        self.instance.save(
            update_fields=[
                "group_identifier",
                "randomized",
                "randomized_datetime",
                "modified",
                "status",
            ]
        )
        self.instance.refresh_from_db()
        self.update_patient_logs_and_consents()

    @property
    def randomization_list_obj(self) -> RandomizationList:
        return get_object_for_subject(
            self.instance.group_identifier,
            "default",
            identifier_fld="group_identifier",
            label="group",
        )

    def update_patient_logs_and_consents(self):
        for patient in self.instance.patients.all():
            self.update_patient_log(patient)
            self.update_subject_consent(patient)
            self.update_registered_subject(patient)

    def update_patient_log(self, patient_log: PatientLog):
        patient_log.group_identifier = self.instance.group_identifier
        patient_log.save(update_fields=["group_identifier"])

    def update_subject_consent(self, patient_log: PatientLog):
        subject_consent = self.subject_consent_model_cls.objects.get(
            subject_identifier=patient_log.subject_identifier
        )
        subject_consent.group_identifier = self.instance.group_identifier
        subject_consent.save(update_fields=["group_identifier"])

    def update_registered_subject(self, patient_log: PatientLog):
        randomization_datetime = self.randomization_list_obj.allocated_datetime
        rs_obj = RegisteredSubject.objects.get(
            subject_identifier=patient_log.subject_identifier
        )
        rs_obj.randomization_datetime = randomization_datetime
        rs_obj.sid = self.randomization_list_obj.sid
        rs_obj.registration_status = RANDOMIZED
        rs_obj.randomization_list_model = self.randomization_list_obj._meta.label_lower
        rs_obj.save(
            update_fields=[
                "randomization_datetime",
                "sid",
                "registration_status",
                "randomization_list_model",
            ]
        )

    @property
    def subject_consent_model_cls(self):
        return django_apps.get_model(self.subject_consent_model)
