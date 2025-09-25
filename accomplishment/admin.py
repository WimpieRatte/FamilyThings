from django.contrib import admin
from .models import Accomplishment, FamilyUserAccomplishment, MeasurementType


# Register your models here.
@admin.register(Accomplishment)
class AccomplishmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_by', 'name', 'icon']
    list_editable = ['name', 'icon']


@admin.register(FamilyUserAccomplishment)
class FamilyUserAccomplishmentAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(MeasurementType)
class MeasurementTypeAdmin(admin.ModelAdmin):
    pass
