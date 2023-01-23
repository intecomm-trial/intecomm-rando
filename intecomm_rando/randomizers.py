from edc_constants.constants import UUID_PATTERN
from edc_randomization.randomizer import Randomizer as Base
from edc_randomization.site_randomizers import site_randomizers

from .constants import CLINIC_CONTROL, COMM_INTERVENTION
from .models import RegisteredGroup


class Randomizer(Base):
    """Randomize a Patient Group.

    Intervention: Integrated Community-based care
    Control: Integrated clinic-based care
    """

    assignment_map = {COMM_INTERVENTION: 1, CLINIC_CONTROL: 2}
    assignment_description_map = {
        COMM_INTERVENTION: "Integrated Community Care",
        CLINIC_CONTROL: "Integrated Clinic-based care",
    }
    trial_is_blinded = False
    model: str = "intecomm_rando.randomizationlist"

    extra_csv_fieldnames = ["description", "facility_type", "country", "version"]

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
