from django.db import models


class Currency(models.Model):
    code = models.CharField(
        primary_key=True,
        unique=True,
        max_length=3
    )
    description = models.CharField(max_length=1000)

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"
