from uuid import uuid4

from django.test import TestCase
from django_mock_queries.query import MockModel, MockSet
from edc_constants.constants import COMPLETE
from edc_randomization.site_randomizers import site_randomizers
from edc_sites.add_or_update_django_sites import add_or_update_django_sites

from intecomm_rando.randomize_group import (
    GroupAlreadyRandomized,
    GroupRandomizationError,
)
from intecomm_rando.randomize_group import RandomizeGroup as BaseRandomizeGroup
from intecomm_rando.randomizers import Randomizer
from intecomm_rando.tests.sites import all_sites


class SubjectScreeningMockModel(MockModel):
    def __init__(self, *args, **kwargs):
        kwargs["mock_name"] = "SubjectScreening"
        super().__init__(*args, **kwargs)
        self._meta.label_lower = "intecomm_screening.subjectscreening"


class PatientGroupMockModel(MockModel):
    def __init__(self, *args, **kwargs):
        kwargs["mock_name"] = "PatientGroup"
        super().__init__(*args, **kwargs)
        self._meta.label_lower = "intecomm_screening.patientgroup"


class PatientLogMockModel(MockModel):
    def __init__(self, *args, **kwargs):
        kwargs["mock_name"] = "PatientLog"
        super().__init__(*args, **kwargs)
        self._meta.label_lower = "intecomm_screening.patientlog"


class ConditionsMockModel(MockModel):
    def __init__(self, *args, **kwargs):
        kwargs["mock_name"] = "Conditions"
        super().__init__(*args, **kwargs)
        self._meta.label_lower = "intecomm_list.conditions"


class RandomizeGroup(BaseRandomizeGroup):
    def create_group_identifier(self):
        return f"999{str(uuid4())[0:10].upper()}"


class RandoTests(TestCase):
    def setUp(self) -> None:
        site_randomizers._registry = {}
        site_randomizers.loaded = False
        site_randomizers.register(Randomizer)
        for country, sites in all_sites.items():
            add_or_update_django_sites(sites=sites, verbose=False)

    def get_patients(self, cnt=None, screen=None, consent=None) -> list:
        patients = []
        for i in range(0, cnt or 14):
            screening_identifier = f"XYZ{str(i)}" if screen else None
            subject_identifier = f"999-{str(i)}" if screen else None
            patients.append(
                PatientLogMockModel(
                    screening_identifier=screening_identifier,
                    subject_identifier=subject_identifier,
                )
            )
        return patients

    def test_ok(self):
        patient_group = PatientGroupMockModel(
            randomized=False,
            group_identifier=str(uuid4()),
            status=COMPLETE,
            patients=MockSet(*self.get_patients()),
        )
        randomizer = RandomizeGroup(patient_group)
        randomizer.randomize_group()

        self.assertTrue(patient_group.group_identifier.startswith("999"))

    def test_already_randomized(self):
        patient_group = PatientGroupMockModel(
            randomized=False,
            group_identifier="99951518883",
            status=COMPLETE,
            patients=MockSet(*self.get_patients()),
        )
        randomizer = RandomizeGroup(patient_group)
        self.assertRaises(GroupAlreadyRandomized, randomizer.randomize_group)

    def test_incomplete_group(self):
        patient_group = PatientGroupMockModel(
            randomized=False,
            group_identifier=str(uuid4()),
            status="BLAH",
            patients=MockSet(*self.get_patients()),
        )
        randomizer = RandomizeGroup(patient_group)
        self.assertRaises(GroupRandomizationError, randomizer.randomize_group)

    def test_complete_group_but_not_enough_members(self):
        patient_group = PatientGroupMockModel(
            randomized=False,
            group_identifier=str(uuid4()),
            status=COMPLETE,
            patients=MockSet(*self.get_patients(10)),
        )
        randomizer = RandomizeGroup(patient_group)
        with self.assertRaises(GroupRandomizationError) as cm:
            randomizer.randomize_group()
        self.assertIn("Patient group must have at least", str(cm.exception))

    def test_complete_group_enough_members_not_screened(self):
        patient_group = PatientGroupMockModel(
            randomized=False,
            group_identifier=str(uuid4()),
            status=COMPLETE,
            patients=MockSet(*self.get_patients(15)),
        )
        randomizer = RandomizeGroup(patient_group)
        with self.assertRaises(GroupRandomizationError) as cm:
            randomizer.randomize_group()
        self.assertIn("Patient has not been screened", str(cm.exception))

    def test_complete_group_enough_members_not_consented(self):
        patient_group = PatientGroupMockModel(
            randomized=False,
            group_identifier=f"GRP-{str(uuid4())}",
            status=COMPLETE,
            patients=MockSet(*self.get_patients(15, screen=True)),
        )
        randomizer = RandomizeGroup(patient_group)
        with self.assertRaises(GroupRandomizationError) as cm:
            randomizer.randomize_group()
        self.assertIn("Patient has not been consented", str(cm.exception))

    def test_complete_group_enough_members_all_consented(self):
        patient_group = PatientGroupMockModel(
            randomized=False,
            group_identifier=None,
            status=COMPLETE,
            patients=MockSet(*self.get_patients(15, screen=True, consent=True)),
        )
        randomizer = RandomizeGroup(patient_group)
        with self.assertRaises(GroupRandomizationError) as cm:
            randomizer.randomize_group()
        self.assertIn("Patient has not been consented", str(cm.exception))
