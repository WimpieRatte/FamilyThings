from django.contrib import admin
from .models import CustomUser, Accomplishment, FamilyUserAccomplishment


# Register your models here.
@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'color', 'background_image']
    list_editable = ['color', 'background_image']


@admin.register(Accomplishment)
class AccomplishmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'icon']
    list_editable = ['name', 'icon']


@admin.register(FamilyUserAccomplishment)
class FamilyUserAccomplishmentAdmin(admin.ModelAdmin):
    list_display = ['id']
