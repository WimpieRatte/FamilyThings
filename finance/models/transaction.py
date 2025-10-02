from django.db import models
from .business_entity import BusinessEntity
from .currency import Currency
from core.models.custom_user import CustomUser
from core.utils import get_first_custom_user


class Transaction(models.Model):
    id = models.BigIntegerField(
        primary_key=True,
        unique=True
        )
    # import_history_id
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    created = models.DateTimeField()
    transaction_date = models.DateTimeField()
    reference = models.CharField(max_length=500)
    business_entity_id = models.ForeignKey(
        BusinessEntity,
        on_delete=models.CASCADE,
        related_name="business_entity_transactions"
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=18
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="currency_transactions"
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="created_transactions",
        default=get_first_custom_user
    )
    # transaction_category_id


    class Meta:
        verbose_name = " Transaction"
        verbose_name_plural = " Transactions"
