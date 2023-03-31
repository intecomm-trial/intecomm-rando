from uuid import uuid4

from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils import get_utcnow


class RegisteredGroupManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, group_identifier_as_pk):
        return self.get(group_identifier_as_pk=group_identifier_as_pk)


class RegisteredGroup(SiteModelMixin, BaseUuidModel):
    registration_datetime = models.DateTimeField(default=get_utcnow)

    group_identifier_as_pk = models.UUIDField(
        max_length=36,
        unique=True,
        help_text="Set to same value from PatientGroup when group is registered",
    )

    group_identifier = models.CharField(
        max_length=36, unique=True, help_text="Updated when group is randomized"
    )

    sid = models.CharField(
        verbose_name="SID",
        max_length=36,
        unique=True,
        default=uuid4,
        help_text=(
            "Default value is UUID for unique constraint. "
            "Updated to a real SID when group is randomized"
        ),
    )

    randomization_datetime = models.DateTimeField(
        null=True, blank=True, help_text="Updated when group is randomized"
    )

    randomization_list_model = models.CharField(
        max_length=150, null=True, help_text="Updated when group is randomized"
    )

    on_site = CurrentSiteManager()

    history = HistoricalRecords()

    objects = RegisteredGroupManager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.group_identifier = self.group_identifier_as_pk
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Registered Group"
        verbose_name_plural = "Registered Groups"
        ordering = ["group_identifier"]
