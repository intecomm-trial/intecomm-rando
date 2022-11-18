from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import CONTROL, INTERVENTION
from edc_randomization.randomizer import AlreadyRandomized, RandomizationError
from edc_randomization.randomizer import Randomizer as Base
from edc_randomization.site_randomizers import site_randomizers

from .models import RegisteredGroup


class Randomizer(Base):
    assignment_map = {INTERVENTION: 1, CONTROL: 2}
    assignment_description_map = {
        INTERVENTION: "intervention",
        CONTROL: "control",
    }
    trial_is_blinded = False
    model: str = "intecomm_rando.randomizationlist"

    def __init__(self, **kwargs):
        self._registered_group = None
        super().__init__(**kwargs)

    @property
    def group_identifier(self):
        return self.subject_identifier

    @property
    def registered_subject(self):
        return self.registered_group

    @property
    def registered_group(self):
        if not self._registered_group:
            try:
                self._registered_group = RegisteredGroup.objects.get(
                    group_identifier=self.group_identifier, sid__isnull=True
                )
            except ObjectDoesNotExist:
                try:
                    obj = RegisteredGroup.objects.get(group_identifier=self.group_identifier)
                except ObjectDoesNotExist:
                    raise RandomizationError(
                        f"Patient Group does not exist. Got {self.group_identifier}"
                    )
                else:
                    raise AlreadyRandomized(
                        "Patient Group already randomized. See RegisteredGroup. "
                        f"Got {obj.group_identifier} "
                        f"SID={obj.sid}",
                        code=RegisteredGroup._meta.label_lower,
                    )
        return self._registered_group


site_randomizers.register(Randomizer)
