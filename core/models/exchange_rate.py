from django.db import models

from .currency import Currency

class ExchangeRate(models.Model):
    id = models.BigIntegerField(
        primary_key=True,
        unique=True
    )
    currency_from = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="currency_from"
    )
    currency_to = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="currency_to"
    )
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()