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
        related_name="accomplishments",
        editable=False
    )
    accomplishment_id = models.ForeignKey(
        Accomplishment,
        on_delete=models.CASCADE,
        related_name="family_user_accomplishments",
        null=True,
        blank=True,
        editable=False
    )
    measurement_quantity = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=2,
        max_digits=18
    )
    created = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    from_date = models.DateTimeField(
        null=True,
        blank=True
    )
    to_date = models.DateTimeField(
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="created_family_user_accomplishments",
        editable=False
    )
    chore_assignment_id = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="chore_completions",
        editable=False
    )

    def serialized(self) -> dict:
        output = self.accomplishment_id.serialized()
        output['created_date'] = self.created.strftime("%Y-%m-%d")
        output['cleared_date'] = self.to_date.strftime("%Y-%m-%d")
        output['measurement_quantity'] = self.measurement_quantity

        return output

    def get_accomplishment(self):
        return self.accomplishment_id

    class Meta:
        verbose_name = " Family User Accomplishment"
        verbose_name_plural = " Family User Accomplishments"
