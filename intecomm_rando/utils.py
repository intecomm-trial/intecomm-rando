from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from edc_appointment.constants import NEW_APPT
from edc_appointment.models import Appointment, AppointmentType
from edc_constants.constants import CLINIC, COMMUNITY
from edc_randomization.utils import get_object_for_subject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from intecomm_rando.constants import COMMUNITY_ARM, FACILITY_ARM

if TYPE_CHECKING:
    from intecomm_screening.models import PatientLog


def get_assignment_for_subject(subject_identifier: str):
    """Replaces default get_assignment_for_subject.

    Note: INTECOMM randomizes by group, not subject
    """
    patient_log_model_cls = django_apps.get_model("intecomm_screening.patientlog")
    patient_log = patient_log_model_cls.objects.get(subject_identifier=subject_identifier)
    rando_obj = get_object_for_subject(
        patient_log.group_identifier, "default", identifier_fld="group_identifier"
    )
    return rando_obj.assignment


def get_assignment_as_appt_type(assignment: str):
    return COMMUNITY if assignment == COMMUNITY_ARM else CLINIC


def update_appt_type_on_new_appointments(
    subject_identifier: str, visit_schedule_name: str, schedule_name: str
):
    """Update appt_type to match rando"""
    assignment = get_assignment_for_subject(subject_identifier)
    Appointment.objects.filter(
        subject_identifier=subject_identifier,
        appt_status=NEW_APPT,
        visit_schedule_name=visit_schedule_name,
        schedule_name=schedule_name,
        appt_type__isnull=True,
    ).update(
        appt_type=AppointmentType.objects.get(name=get_assignment_as_appt_type(assignment))
    )


def update_patient_in_newly_randomized_group(
    patient: PatientLog,
    assignment: str,
    randomization_datetime: datetime,
    skip_get_current_site: bool | None = None,
):
    if assignment in [COMMUNITY_ARM, FACILITY_ARM]:
        model_name = (
            "intecomm_prn.onschedulecomm"
            if assignment == COMMUNITY_ARM
            else "intecomm_prn.onscheduleinte"
        )
        visit_schedule, schedule = site_visit_schedules.get_by_onschedule_model(model_name)
        schedule.put_on_schedule(
            subject_identifier=patient.subject_identifier,
            onschedule_datetime=randomization_datetime,
            skip_get_current_site=skip_get_current_site,
        )
        update_appt_type_on_new_appointments(
            subject_identifier=patient.subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
        )
