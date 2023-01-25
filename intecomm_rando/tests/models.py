from django.db import models
from edc_model.models import BaseUuidModel


class SubjectConsent(BaseUuidModel):

    group_identifier = models.CharField(max_length=50)

    subject_identifier = models.CharField(max_length=50, unique=True)
