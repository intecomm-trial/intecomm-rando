import re

from django.db.models.signals import post_save
from django.dispatch import receiver
from edc_constants.constants import COMPLETE, UUID_PATTERN, YES
from edc_randomization.randomizer import RandomizationError

from ..randomize_group import randomize_group


@receiver(
    post_save,
    weak=False,
    dispatch_uid="randomize_group_on_post_save",
)
def randomize_patient_group_on_post_save(sender, instance, raw, **kwargs):
    if not raw and instance and instance._meta.label_lower.split(".")[1] == "patientgroup":
        if (
            not instance.randomized
            and instance.randomize_now == YES
            and instance.confirm_randomize_now == "RANDOMIZE"
            and instance.status == COMPLETE
        ):
            if not re.match(UUID_PATTERN, instance.group_identifier):
                raise RandomizationError(
                    "Failed to randomize group. Group identifier is not a uuid. "
                    f"Has this group already been randomized? Got {instance.group_identifier}."
                )
            randomize_group(instance)
