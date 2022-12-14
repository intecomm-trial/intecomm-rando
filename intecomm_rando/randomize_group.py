from __future__ import annotations

from typing import TYPE_CHECKING

from edc_constants.constants import COMPLETE, YES
from edc_randomization.site_randomizers import site_randomizers
from edc_utils import get_utcnow

from .exceptions import GroupAlreadyRandomized, GroupRandomizationError
from .group_eligibility import assess_group_eligibility
from .group_identifier import GroupIdentifier

if TYPE_CHECKING:
    from intecomm_screening.models import PatientGroup


def randomize_group(instance: PatientGroup) -> None:
    rando = RandomizeGroup(instance)
    rando.randomize_group()


class RandomizeGroup:

    min_group_size = 14

    def __init__(self, instance: PatientGroup):
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
        self.instance.modified = report_datetime
        self.instance.save(
            update_fields=[
                "group_identifier",
                "randomized",
                "modified",
            ]
        )
        self.instance.refresh_from_db()
