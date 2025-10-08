from django.db import models
from core.models.custom_user import CustomUser
from accomplishment.models.accomplishment import Accomplishment
from core.utils import get_first_custom_user


class Chore(models.Model):
    id = models.BigIntegerField(
        primary_key=True,
        unique=True
        )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="created_chores",
        default=get_first_custom_user
    )
    created = models.DateTimeField()
    description = models.CharField(max_length=1000)
    frequency = models.CharField(max_length=100)
    accomplishment_id = models.ForeignKey(
        Accomplishment,
        on_delete=models.CASCADE,
        related_name='accomplishment_chores'
    )

    class Meta:
        verbose_name = "Chore"
        verbose_name_plural = "Chores"
