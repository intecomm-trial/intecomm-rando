from __future__ import annotations

from intecomm_form_validators.utils import (
    PatientGroupMakeupError,
    PatientGroupRatioError,
    PatientGroupSizeError,
    PatientNotConsentedError,
    PatientNotScreenedError,
    PatientNotStableError,
    confirm_patient_group_minimum_of_each_condition_or_raise,
    confirm_patient_group_ratio_or_raise,
    confirm_patient_group_size_or_raise,
    confirm_patients_stable_and_screened_and_consented_or_raise,
)

from .exceptions import GroupRandomizationError


def assess_group_eligibility(instance, called_by_rando: bool | None = None):
    group_eligibility = GroupEligibility(instance, called_by_rando=called_by_rando)
    group_eligibility.assess()


class GroupEligibility:
    def __init__(self, instance, called_by_rando: bool | None = None):
        self.instance = instance
        self.called_by_rando = called_by_rando

    def assess(self):
        self.confirm_patients_stable_and_screened_and_consented_or_raise()
        self.confirm_patient_group_size_or_raise()
        self.confirm_patient_group_minimum_of_each_condition_or_raise()
        self.confirm_patient_group_ratio_or_raise()

    def confirm_patients_stable_and_screened_and_consented_or_raise(self):
        try:
            confirm_patients_stable_and_screened_and_consented_or_raise(
                patients=self.instance.patients
            )
        except (PatientNotStableError, PatientNotScreenedError, PatientNotConsentedError) as e:
            if self.called_by_rando:
                raise GroupRandomizationError(e)
            raise

    def confirm_patient_group_minimum_of_each_condition_or_raise(self):
        try:
            confirm_patient_group_minimum_of_each_condition_or_raise(
                patients=self.instance.patients,
            )
        except PatientGroupMakeupError as e:
            if self.called_by_rando:
                raise GroupRandomizationError(e)
            raise

    def confirm_patient_group_size_or_raise(self):
        try:
            confirm_patient_group_size_or_raise(
                bypass_group_size_min=self.instance.bypass_group_size_min,
                patients=self.instance.patients,
            )
        except PatientGroupSizeError as e:
            if self.called_by_rando:
                raise GroupRandomizationError(e)
            raise

    def confirm_patient_group_ratio_or_raise(self):
        try:
            confirm_patient_group_ratio_or_raise(
                patients=self.instance.patients.all(),
                bypass_group_ratio=self.instance.bypass_group_ratio,
            )
        except PatientGroupRatioError as e:
            if self.called_by_rando:
                raise GroupRandomizationError(e)
            raise
