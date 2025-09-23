from django.db import models
from .business_entity import BusinessEntity
from .currency import Currency


class Transaction(models.Model):
    id = models.BigIntegerField(
        primary_key=True,
        unique=True
        )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    created = models.DateTimeField()
    transaction_date = models.DateTimeField()
    reference = models.CharField(max_length=500)
    business_entity_id = models.ForeignKey(
        BusinessEntity,
        on_delete=models.CASCADE,
        related_name="business_entity_id"
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=18
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="currency"
    )

    class Meta:
        verbose_name = " Transaction"
        verbose_name_plural = " Transactions"
