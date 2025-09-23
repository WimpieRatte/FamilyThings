from django.contrib import admin
from .models import BusinessEntity, Currency, ExchangeRate, Transaction


# Register your models here.
@admin.register(BusinessEntity)
class BusinessEntityAdmin(admin.ModelAdmin):
    pass


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    pass


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass
