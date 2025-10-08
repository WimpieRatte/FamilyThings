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
        related_name="accomplishments"
    )
    accomplishment_id = models.ForeignKey(
        Accomplishment,
        on_delete=models.CASCADE,
        related_name="family_user_accomplishments"
    )
    measurement_quantity = models.BigIntegerField(
        null=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="created_family_user_accomplishments"
    )
    chore_assignment_id = models.ForeignKey(
        CustomUser,
        null=True,
        on_delete=models.CASCADE,
        related_name="chore_completions"
    )

    def get_accomplishment(self):
        return self.accomplishment_id

    class Meta:
        verbose_name = " Family User Accomplishment"
        verbose_name_plural = " Family User Accomplishments"
