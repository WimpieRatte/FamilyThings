import uuid
from django.db import models


class Family(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)

    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"
