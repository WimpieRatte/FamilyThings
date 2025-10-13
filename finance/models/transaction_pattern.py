from django.db import models

class TransactionPattern(models.Model):
    id = models.AutoField(primary_key=True)
    name_regex = models.CharField(max_length=1000)
    description_regex = models.CharField(max_length=1000)
    reference_regex = models.CharField(max_length=1000)
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=18
    )
    transaction_category_id = models.ForeignKey('TransactionCategory', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Transaction Category"
        verbose_name_plural = "Transaction Categories"
