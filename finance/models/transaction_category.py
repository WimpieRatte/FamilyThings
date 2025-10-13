from django.db import models

class TransactionCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=1000)

    class Meta:
        verbose_name = "Transaction Category"
        verbose_name_plural = "Transaction Categories"
