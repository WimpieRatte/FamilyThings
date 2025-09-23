import uuid
from django.db import models


class AccomplishmentType(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)

    class Meta:
        verbose_name = "Accomplishment Type"
        verbose_name_plural = "Accomplishment Types"
