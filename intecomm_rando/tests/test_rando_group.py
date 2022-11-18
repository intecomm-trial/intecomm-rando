from uuid import uuid4

from django.test import TestCase
from django_mock_queries.query import MockModel, MockSet
from edc_constants.constants import COMPLETE

from intecomm_rando.randomize_group import RandomizeGroup


class SubjectScreeningMockModel(MockModel):
    def __init__(self, *args, **kwargs):
        kwargs["mock_name"] = "SubjectScreening"
        super().__init__(*args, **kwargs)


class PatientGroupMockModel(MockModel):
    def __init__(self, *args, **kwargs):
        kwargs["mock_name"] = "PatientGroup"
        super().__init__(*args, **kwargs)


class PatientLogMockModel(MockModel):
    def __init__(self, *args, **kwargs):
        kwargs["mock_name"] = "PatientLog"
        super().__init__(*args, **kwargs)


class ConditionsMockModel(MockModel):
    def __init__(self, *args, **kwargs):
        kwargs["mock_name"] = "Conditions"
        super().__init__(*args, **kwargs)


class RandoTests(TestCase):
    def test_ok(self):
        patient_group = PatientGroupMockModel(
            randomized=False, group_identifier=uuid4(), status=COMPLETE, patients=MockSet()
        )
        randomizer = RandomizeGroup(patient_group)
        randomizer.randomize_group()
