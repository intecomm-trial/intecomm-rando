from edc_constants.constants import CONTROL, INTERVENTION, UUID_PATTERN
from edc_randomization.randomizer import Randomizer as Base
from edc_randomization.site_randomizers import site_randomizers

from .models import RegisteredGroup


class Randomizer(Base):
    """Randomize a Patient Group.

    Intevention: Integrated Community-based care
    Control: Integrated clinic-based care
    """

    assignment_map = {INTERVENTION: 1, CONTROL: 2}
    assignment_description_map = {
        INTERVENTION: "intervention",
        CONTROL: "control",
    }
    trial_is_blinded = False
    model: str = "intecomm_rando.randomizationlist"

    def __init__(self, **kwargs):
        kwargs["identifier_attr"] = "group_identifier"
        kwargs["identifier_object_name"] = "patient group"
        super().__init__(**kwargs)

    @classmethod
    def get_registration_model_cls(cls):
        return RegisteredGroup

    def get_unallocated_registration_obj(self):
        return self.get_registration_model_cls().objects.get(
            **dict(sid__regex=UUID_PATTERN.pattern), **self.identifier_opts
        )


site_randomizers.register(Randomizer)
