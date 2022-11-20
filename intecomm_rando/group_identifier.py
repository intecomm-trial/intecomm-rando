from django.apps import apps as django_apps
from edc_identifier.research_identifier import ResearchIdentifier
from edc_utils import get_utcnow


class GroupIdentifier(ResearchIdentifier):
    """Create and save unique group identifier.

    Creates and updates the RegisteredGroup model with the newly
    created GroupIdentifier.
    """

    template: str = "{site_id}{sequence}"
    label: str = "groupidentifier"
    padding: int = 4

    def __init__(self, group_identifier_as_pk=None, **kwargs):
        self.group_identifier_as_pk = group_identifier_as_pk
        super().__init__(**kwargs)

    def pre_identifier(self) -> None:
        pass

    def post_identifier(self) -> None:
        """Creates a registered group instance for this
        group identifier.
        """
        model_cls = django_apps.get_model("intecomm_rando.registeredgroup")
        obj = model_cls.objects.create(
            group_identifier_as_pk=self.group_identifier_as_pk,
            site=self.site,
            registration_datetime=get_utcnow(),
        )
        obj.group_identifier = self.identifier
        obj.save()
