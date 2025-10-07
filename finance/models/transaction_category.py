from django.db import models

class TransactionCategory(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)

    class Meta:
        verbose_name = "Transaction Category"
        verbose_name_plural = "Transaction Categories"
