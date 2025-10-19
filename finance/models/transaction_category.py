from django.db import models
from core.models import Family
import uuid

class TransactionCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    family_id = models.ForeignKey(Family,
                                  on_delete=models.CASCADE,
                                  default=uuid.uuid4)

    class Meta:
        verbose_name = "Transaction Category"
        verbose_name_plural = "Transaction Categories"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "family_id"],
                name="unique_transaction_category_per_family"
            )
        ]