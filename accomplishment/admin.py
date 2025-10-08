from django.contrib import admin
from .models import Accomplishment, FamilyUserAccomplishment, AccomplishmentType, MeasurementType


# Register your models here.
@admin.register(Accomplishment)
class AccomplishmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_by', 'name', 'icon']
    list_editable = ['name', 'icon']


@admin.register(FamilyUserAccomplishment)
class FamilyUserAccomplishmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'accomplishment_id', 'accomplishment_name', 'created_by']

    def accomplishment_name(self, obj: FamilyUserAccomplishment):
        return obj.accomplishment_id.name


@admin.register(AccomplishmentType)
class AccomplishmentTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(MeasurementType)
class MeasurementTypeAdmin(admin.ModelAdmin):
    pass
