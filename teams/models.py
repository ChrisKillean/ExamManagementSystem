from django.db import models
from django.conf import settings


# Model for teams
class Team(models.Model):
    team_name = models.CharField(
        null=False,
        max_length=100,
        unique=True,
    )
    exam_setter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        on_delete=models.PROTECT,
        related_name='exam_setter_set',
    )
    internal_reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        on_delete=models.PROTECT,
        related_name='internal_reviewer_set',
    )
    vetting_committee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        on_delete=models.PROTECT,
        related_name='vetting_committee_set',
    )
    external_examiner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        on_delete=models.PROTECT,
        related_name='external_reviewer_set',
    )
    school_office = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        on_delete=models.PROTECT,
        related_name='school_office_set',
    )
    observer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name='observer_set',
    )
    active = models.BooleanField(
        default=True,
        null=False,
        editable=True,
    )

    def __str__(self):
        return self.team_name
