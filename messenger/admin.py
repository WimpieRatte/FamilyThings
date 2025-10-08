from django.contrib import admin
from .models import FamilyChat, Message


# Register your models here.
@admin.register(FamilyChat)
class FamilyChatAdmin(admin.ModelAdmin):
    pass



@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass
