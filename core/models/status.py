from django.db import models

class Status(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statusses"
