import re

from django.db.models.signals import post_save
from django.dispatch import receiver
from edc_constants.constants import COMPLETE, UUID_PATTERN, YES
from edc_randomization.constants import RANDOMIZED
from edc_randomization.randomizer import RandomizationError
from edc_randomization.utils import get_object_for_subject
from edc_registration.models import RegisteredSubject

from ..randomize_group import randomize_group


@receiver(
    post_save,
    weak=False,
    dispatch_uid="randomize_group_on_post_save",
)
def randomize_patient_group_on_post_save(sender, instance, raw, **kwargs):
    """Randomize a patient group if ready and not already randomized."""
    if not raw and instance and instance._meta.label_lower.split(".")[1] == "patientgroup":
        if (
            not instance.randomized
            and instance.randomize_now == YES
            and instance.confirm_randomize_now == "RANDOMIZE"
            and instance.status == COMPLETE
        ):
            if not re.match(UUID_PATTERN, str(instance.group_identifier)):
                raise RandomizationError(
                    "Failed to randomize group. Group identifier is not a uuid. "
                    f"Has this group already been randomized? Got {instance.group_identifier}."
                )
            randomize_group(instance)
            rando_obj = get_object_for_subject(
                instance.group_identifier, "default", identifier_fld="group_identifier"
            )
            randomization_datetime = rando_obj.allocated_datetime
            for patient in instance.patients.all():
                rs_obj = RegisteredSubject.objects.get(
                    subject_identifier=patient.subject_identifier
                )
                rs_obj.randomization_datetime = randomization_datetime
                rs_obj.sid = rando_obj.sid
                rs_obj.registration_status = RANDOMIZED
                rs_obj.randomization_list_model = rando_obj._meta.label_lower
                rs_obj.save(
                    update_fields=[
                        "randomization_datetime",
                        "sid",
                        "registration_status",
                        "randomization_list_model",
                    ]
                )
