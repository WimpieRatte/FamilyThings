from django.db import models
from django.urls import reverse
from core.models import Family
import uuid

def get_first_family():
    return Family.objects.first().id

class TransactionCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    family_id = models.ForeignKey(Family,
                                  on_delete=models.CASCADE,
                                  default=get_first_family)

    class Meta:
        verbose_name = "Transaction Category"
        verbose_name_plural = "Transaction Categories"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "family_id"],
                name="unique_transaction_category_per_family"
            )
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('finance:transaction_category_list')

    def get_edit_url(self):
        return reverse('finance:transaction_category_edit', args=[self.pk])

    def get_delete_url(self):
        return reverse('finance:transaction_category_delete', args=[self.pk])