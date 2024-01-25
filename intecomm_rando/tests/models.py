from django.db import models
from edc_model.models import BaseUuidModel
from edc_sites.model_mixins import SiteModelMixin


class SubjectConsent(SiteModelMixin, BaseUuidModel):
    group_identifier = models.CharField(max_length=50)

    subject_identifier = models.CharField(max_length=50, unique=True)
