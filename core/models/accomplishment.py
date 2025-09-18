import uuid
from django.db import models

from .family_user import FamilyUser
from .accomplishment_type import AccomplishmentType
from .measurement_type import MeasurementType


class Accomplishment(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    created = models.DateTimeField()
    created_by = models.ForeignKey(
        FamilyUser,
        on_delete=models.CASCADE,
        related_name="custom_user_id"
    )
    accomplishment_type_id = models.ForeignKey(
        AccomplishmentType,
        on_delete=models.CASCADE,
        related_name="accomplishment_type_id"
    )
    measurement_type_id = models.ForeignKey(
        MeasurementType,
        on_delete=models.CASCADE,
        related_name="measurement_type_id"
    )
    