from django.contrib import admin
from .models import CustomUser, FamilyUser, Family, FamilyInvite


# Register your models here.
@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'birthday', 'color', 'icon', 'background_image']
    list_editable = ['color', 'icon', 'background_image']


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    pass

@admin.register(FamilyInvite)
class FamilyInviteAdmin(admin.ModelAdmin):
    pass


@admin.register(FamilyUser)
class FamilyUserAdmin(admin.ModelAdmin):
    list_display = ['family_id__name', 'custom_user_id__username', 'custom_user_id__username']