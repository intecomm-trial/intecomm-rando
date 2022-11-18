from __future__ import annotations

import re

from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import COMPLETE, UUID_PATTERN
from edc_utils import get_utcnow

from .group_identifier import GroupIdentifier


class GroupAlreadyRandomized(Exception):
    pass


class GroupRandomizationError(Exception):
    pass


def randomize_group(instance):
    rando = RandomizeGroup(instance)
    rando.randomize_group()


class RandomizeGroup:
    def __init__(self, instance, screening_model_cls=None, consent_model_cls=None):
        self.instance = instance
        self.screening_model_cls = screening_model_cls
        self.consent_model_cls = consent_model_cls

    def randomize_group(self):
        if self.instance.randomized:
            raise GroupAlreadyRandomized(f"Group is already randomized. Got {self.instance}.")
        if not re.match(UUID_PATTERN, str(self.instance.group_identifier)):
            raise GroupAlreadyRandomized(
                "Randomization failed. Group identifier already set. "
                f"See {self.instance.group_identifier}."
            )
        if self.instance.status != COMPLETE:
            raise GroupRandomizationError(f"Group is not complete. Got {self.instance}.")
        for patient_log in self.instance.patients.all():
            if not patient_log.screening_identifier:
                raise GroupRandomizationError(
                    f"Patient has not been screened. Got {patient_log}. (1)"
                )
            if not patient_log.subject_identifier:
                raise GroupRandomizationError(
                    f"Patient has not consented. Got {patient_log} (1)."
                )

            # check screening model / eligibility
            self.check_eligibility(patient_log)

            # redundantly check consent model
            try:
                self.consent_model_cls.objects.get(
                    subject_identifier=patient_log.subject_identifier
                )
            except ObjectDoesNotExist:
                raise GroupRandomizationError(
                    f"Patient has not consented. Got {patient_log} (2)."
                )

        self.randomize()

        return True, get_utcnow(), self.instance.user_modified, self.create_group_identifier()

    def randomize(self):
        pass

    def check_eligibility(self, patient_log):
        try:
            obj = self.screening_model_cls.objects.get(
                subject_identifier=patient_log.screening_identifier
            )
        except ObjectDoesNotExist:
            raise GroupRandomizationError(
                f"Patient has not been screened. Got {patient_log}. (2)"
            )
        else:
            if not obj.eligible:
                raise GroupRandomizationError(f"Patient is not eligible. Got {obj}.")

    def create_group_identifier(self):
        # create group identifierf
        self.instance.group_identifier = GroupIdentifier(
            identifier_type="patient_group",
            requesting_model=self.instance._meta.label_lower,
            site=self.instance.site,
        ).identifier
