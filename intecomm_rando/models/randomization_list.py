from edc_model.models import BaseUuidModel
from edc_randomization.model_mixins import RandomizationListModelMixin


class RandomizationList(RandomizationListModelMixin, BaseUuidModel):
    class Meta(RandomizationListModelMixin.Meta, BaseUuidModel.Meta):
        pass
