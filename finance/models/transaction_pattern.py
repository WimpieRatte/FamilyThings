from django.db import models
from . import TransactionCategory

class TransactionPattern(models.Model):
    id = models.AutoField(primary_key=True)
    name_regex = models.CharField(max_length=1000, blank=True, null=True)
    description_regex = models.CharField(max_length=1000, blank=True, null=True)
    reference_regex = models.CharField(max_length=1000, blank=True, null=True)
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=18,
        blank=True, null=True
    )
    transaction_category_id = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE, related_name="transaction_patterns")

    class Meta:
        verbose_name = "Transaction Category"
        verbose_name_plural = "Transaction Categories"
