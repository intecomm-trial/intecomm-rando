from django.apps import apps as django_apps
from edc_randomization.utils import get_object_for_subject


def get_assignment_for_subject(subject_identifier):
    """Replaces default get_assignment_for_subject.

    Note: INTECOMM randomizes by group, not subject
    """
    patient_log_model_cls = django_apps.get_model("intecomm_screening.patientlog")
    patient_log = patient_log_model_cls.objects.get(subject_identifier=subject_identifier)
    rando_obj = get_object_for_subject(
        patient_log.group_identifier, "default", identifier_fld="group_identifier"
    )
    return rando_obj.assignment
