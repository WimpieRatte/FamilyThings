from django.db import models
from .currency import Currency


class ExchangeRate(models.Model):
    id = models.AutoField(primary_key=True)
    currency_from = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="exchangerates_from"
    )
    currency_to = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="exchangerates_to"
    )
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()

    class Meta:
        verbose_name = "Exchange Rate"
        verbose_name_plural = "Exchange Rates"
