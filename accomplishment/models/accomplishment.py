import uuid
from django.db import models
from django.utils import timezone

from core.models.family_user import FamilyUser
from .accomplishment_type import AccomplishmentType
from .measurement_type import MeasurementType


class Accomplishment(models.Model):
    id = models.BigIntegerField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    icon = models.CharField(max_length=20, blank=True, default="")
    created = models.DateTimeField(
        default=timezone.now
    )
    created_by = models.ForeignKey(
        FamilyUser,
        on_delete=models.PROTECT,
        # related_name="custom_user_id"  #TODO: Find a different name
        blank=True  # TODO: strip out once debugging is finished
    )
    type = models.ForeignKey(
        AccomplishmentType,
        on_delete=models.PROTECT,
        related_name="accomplishment_type",
        default=None,
        blank=True,
        null=True  # TODO: strip out once debugging is finished
    )
    measurement = models.ForeignKey(
        MeasurementType,
        on_delete=models.PROTECT,
        related_name="measurement_type",
        default=None,
        blank=True,
        null=True  # TODO: strip out once debugging is finished
    )

    class Meta:
        # White space as workaround for the ordering.
        verbose_name = "  Accomplishment"
        verbose_name_plural = "  Accomplishments"
