from django.db import models
from core.models import Family


class ImportProfile(models.Model):
    id = models.AutoField(
        primary_key=True
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    family_id = models.ForeignKey(Family, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Import Profile"
        verbose_name_plural = "Import Profiles"

        constraints = [
            models.UniqueConstraint(
                fields=["name", "family_id"],
                name="unique_import_profile_per_family"
            )
        ]