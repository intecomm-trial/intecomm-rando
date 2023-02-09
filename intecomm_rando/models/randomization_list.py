from django.db import models
from edc_model.models import BaseUuidModel
from edc_randomization.model_mixins import RandomizationListModelMixin


class RandomizationList(RandomizationListModelMixin, BaseUuidModel):
    group_identifier = models.CharField(
        verbose_name="Group Identifier", max_length=50, null=True, unique=True
    )

    def __str__(self):
        return f"{self.site_name}.{self.sid} Group={self.group_identifier}"

    class Meta(RandomizationListModelMixin.Meta, BaseUuidModel.Meta):
        pass
