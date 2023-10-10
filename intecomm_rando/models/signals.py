import re

from django.db.models.signals import post_save
from django.dispatch import receiver
from edc_constants.constants import COMPLETE, UUID_PATTERN, YES
from edc_randomization.constants import RANDOMIZED
from edc_randomization.randomizer import RandomizationError
from edc_randomization.utils import get_object_for_subject
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..constants import COMMUNITY_ARM, FACILITY_ARM
from ..randomize_group import RandomizeGroup


@receiver(
    post_save,
    weak=False,
    dispatch_uid="randomize_group_on_post_save",
)
def randomize_patient_group_on_post_save(sender, instance, raw, **kwargs):
    """Randomize a patient group if ready and not already randomized.

    Note: may be called by the model or its proxy.
    """
    if (
        not raw
        and instance
        and instance._meta.label_lower.split(".")[1] == "patientgrouprando"
    ):
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

            rando = RandomizeGroup(instance)
            _, _, _, group_identifier = rando.randomize_group()

            rando_obj = get_object_for_subject(
                group_identifier, "default", identifier_fld="group_identifier"
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
                if rando_obj.assignment in [COMMUNITY_ARM, FACILITY_ARM]:
                    model_name = (
                        "intecomm_prn.onschedulecomm"
                        if rando_obj.assignment == COMMUNITY_ARM
                        else "intecomm_prn.onscheduleinte"
                    )
                    _, schedule = site_visit_schedules.get_by_onschedule_model(model_name)
                    schedule.put_on_schedule(
                        subject_identifier=patient.subject_identifier,
                        onschedule_datetime=randomization_datetime,
                    )
