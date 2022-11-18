from __future__ import annotations

import re

from edc_constants.constants import COMPLETE, UUID_PATTERN
from edc_randomization.site_randomizers import site_randomizers
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

    min_group_size = 14

    def __init__(self, instance):
        self.instance = instance

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

        if self.instance.patients.all().count() < self.min_group_size:
            raise GroupRandomizationError(
                f"Patient group must have at least {self.min_group_size} members."
            )

        for patient_log in self.instance.patients.all():
            if not patient_log.screening_identifier:
                raise GroupRandomizationError(
                    f"Patient has not been screened. Got {patient_log}. (1)"
                )
            if not patient_log.subject_identifier:
                raise GroupRandomizationError(
                    f"Patient has not consented. Got {patient_log} (1)."
                )

        self.randomize()

        return True, get_utcnow(), self.instance.user_modified, self.create_group_identifier()

    def randomize(self):
        site_randomizers.randomize(
            "default",
            subject_identifier=self.instance.group_identifier,
            report_datetime=get_utcnow(),
            site=self.instance.site,
            user=self.instance.user_created,
        )

    def create_group_identifier(self):
        # create group identifier
        self.instance.group_identifier = GroupIdentifier(
            identifier_type="patient_group",
            requesting_model=self.instance._meta.label_lower,
            site=self.instance.site,
        ).identifier
