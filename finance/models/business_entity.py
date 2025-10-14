from django.db import models
from core.models import Family
import uuid


class BusinessEntity(models.Model):
    id = models.AutoField(
        primary_key=True
        )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    family_id = models.ForeignKey(Family,
                                  on_delete=models.CASCADE,
                                  default=uuid.uuid4)

    class Meta:
        verbose_name = "Business Entity"
        verbose_name_plural = "Business Entities"
