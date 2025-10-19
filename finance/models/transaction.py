from django.db import models
from .business_entity import BusinessEntity
from .currency import Currency
from core.models.custom_user import CustomUser
from core.utils import get_first_custom_user
from finance.models.import_history import ImportHistory


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    import_history_id = models.ForeignKey(
        ImportHistory,
        on_delete=models.CASCADE,
        related_name="imported_transactions",
        default=None, null=True
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
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
    transaction_category_id = models.ForeignKey(
        'TransactionCategory',
        on_delete=models.CASCADE,
        related_name='transactions',
        default=None, null=True
    )


    class Meta:
        verbose_name = " Transaction"
        verbose_name_plural = " Transactions"
