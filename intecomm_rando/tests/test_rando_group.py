from django.test import TestCase

from intecomm_rando.randomize_group import RandomizeGroup


class RandoTests(TestCase):
    def test_ok(self):
        RandomizeGroup()
