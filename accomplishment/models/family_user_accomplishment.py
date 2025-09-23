import uuid
from django.db import models

from core.models.family_user import FamilyUser
from core.models.custom_user import CustomUser
from .accomplishment import Accomplishment


class FamilyUserAccomplishment(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    family_user_id = models.ForeignKey(
        FamilyUser,
        on_delete=models.CASCADE,
        related_name="family_user"
    )
    accomplishment_id = models.ForeignKey(
        Accomplishment,
        on_delete=models.CASCADE,
        related_name="accomplishment_id"
    )
    measurement_quantity = models.BigIntegerField()
    created = models.DateTimeField(
        auto_now_add=True
    )
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="custom_user_id"
    )

    class Meta:
        verbose_name = " Family User Accomplishment"
        verbose_name_plural = " Family User Accomplishments"
