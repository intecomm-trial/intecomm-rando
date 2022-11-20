from __future__ import annotations

from edc_constants.constants import COMPLETE, YES
from edc_randomization.site_randomizers import site_randomizers
from edc_utils import get_utcnow
from intecomm_form_validators.utils import (
    PatientGroupSizeError,
    PatientNotConsentedError,
    PatientNotScreenedError,
    PatientNotStableError,
    confirm_patient_group_ratio_or_raise,
    confirm_patient_group_size_or_raise,
    confirm_patients_stable_and_screened_and_consented_or_raise,
)

from intecomm_rando.group_identifier import GroupIdentifier


class GroupAlreadyRandomized(Exception):
    pass


class GroupRandomizationError(Exception):
    pass


def randomize_group(instance) -> None:
    rando = RandomizeGroup(instance)
    rando.randomize_group()


class RandomizeGroup:

    min_group_size = 14

    def __init__(self, instance):
        self.instance = instance

    def randomize_group(self):
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
        self.confirm_patients_stable_and_screened_and_consented_or_raise()
        self.confirm_patient_group_size_or_raise()
        self.confirm_patient_group_ratio_or_raise()
        self.randomize()
        return True, get_utcnow(), self.instance.user_modified, self.instance.group_identifier

    def confirm_patients_stable_and_screened_and_consented_or_raise(self):
        try:
            confirm_patients_stable_and_screened_and_consented_or_raise(
                patients=self.instance.patients
            )
        except (PatientNotStableError, PatientNotScreenedError, PatientNotConsentedError) as e:
            raise GroupRandomizationError(e)

    def confirm_patient_group_size_or_raise(self):
        try:
            confirm_patient_group_size_or_raise(
                enforce_group_size_min=self.instance.enforce_group_size_min,
                patients=self.instance.patients,
            )
        except PatientGroupSizeError as e:
            raise GroupRandomizationError(e)

    def confirm_patient_group_ratio_or_raise(self):
        confirm_patient_group_ratio_or_raise(
            patients=self.instance.patients,
            enforce_ratio=self.instance.enforce_ratio,
        )

    def randomize(self) -> None:
        identifier_obj = GroupIdentifier(
            identifier_type="patient_group",
            group_identifier_as_pk=self.instance.group_identifier_as_pk,
            requesting_model=self.instance._meta.label_lower,
            site=self.instance.site,
        )
        report_datetime = get_utcnow()
        site_randomizers.randomize(
            "default",
            identifier=identifier_obj.identifier,
            report_datetime=report_datetime,
            site=self.instance.site,
            user=self.instance.user_created,
        )
        self.instance.group_identifier = identifier_obj.identifier
        self.instance.randomized = True
        self.instance.modified = report_datetime
        self.instance.save(
            update_fields=[
                "group_identifier",
                "randomized",
                "modified",
            ]
        )
        self.instance.refresh_from_db()
