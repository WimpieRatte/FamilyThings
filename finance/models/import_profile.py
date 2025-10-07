from django.db import models
from core.models import Family


class ImportProfile(models.Model):
    id = models.IntegerField(
        primary_key=True,
        unique=True
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    family_id = models.ForeignKey(Family, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Import Profile"
        verbose_name_plural = "Import Profiles"
