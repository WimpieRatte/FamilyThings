from django.db import models

class BusinessEntity(models.Model):
    id = models.BigIntegerField(
        primary_key=True,
        unique=True
        )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)