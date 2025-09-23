from django.contrib import admin
from .models import CustomUser, FamilyUser, Family


# Register your models here.
@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'color', 'background_image']
    list_editable = ['color', 'background_image']


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    pass


@admin.register(FamilyUser)
class FamilyUserAdmin(admin.ModelAdmin):
    pass
