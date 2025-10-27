from django.db import models
from django.urls import reverse
from . import TransactionCategory
from core.models.family import Family


def get_first_family():
    return Family.objects.first().id


class TransactionPattern(models.Model):
    id = models.AutoField(primary_key=True)
    business_entity_name = models.CharField(max_length=1000, blank=True, null=True)
    transaction_category_id = models.ForeignKey(TransactionCategory, on_delete=models.PROTECT, related_name="transaction_patterns_of_category")
    family_id = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='family_transaction_patterns', default=get_first_family)

    class Meta:
        verbose_name = "Transaction Category"
        verbose_name_plural = "Transaction Categories"

    def __str__(self):
        return self.business_entity_name

    def get_absolute_url(self):
        return reverse('finance:transaction_pattern_list')

    def get_edit_url(self):
        return reverse('finance:transaction_pattern_edit', args=[self.pk])

    def get_delete_url(self):
        return reverse('finance:transaction_pattern_delete', args=[self.pk])