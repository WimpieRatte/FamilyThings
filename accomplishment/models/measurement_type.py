import uuid
from django.db import models


class MeasurementType(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    abbreviation = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Measurement Type"
        verbose_name_plural = "Measurement Types"
