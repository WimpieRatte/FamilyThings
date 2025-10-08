from django.db import models
from django.utils import timezone

from core.models.family_user import CustomUser
from .accomplishment_type import AccomplishmentType
from .measurement_type import MeasurementType
from core.utils import get_first_custom_user


class Accomplishment(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    icon = models.CharField(max_length=20, blank=True, default="")
    created = models.DateTimeField(
        default=timezone.now
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="custom_user_created_accomplishments",
        default=get_first_custom_user
    )
    accomplishment_type_id = models.ForeignKey(
        AccomplishmentType,
        on_delete=models.PROTECT,
        related_name="accomplishments",
        default=None,
        blank=True,
        null=True
    )
    measurement_type_id = models.ForeignKey(
        MeasurementType,
        on_delete=models.PROTECT,
        related_name="measurements",
        default=None,
        blank=True,
        null=True
    )
    is_achievement = models.BooleanField(default=False)

    def dict(self):
        output: dict = {
            'ID': self.id,
            'name': self.name, 'description': self.description,
            'icon': self.icon, 'is_achievement': self.is_achievement,
            'measurement': self.measurement_type_id,
        }

        if self.accomplishment_type_id:
            output['type'] = str(self.accomplishment_type_id.name).replace("None", "-"),
        return output

    class Meta:
        # White space as workaround for the ordering.
        verbose_name = "  Accomplishment"
        verbose_name_plural = "  Accomplishments"
