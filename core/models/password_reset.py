import uuid
from django.db import models
from django.utils import timezone
from .custom_user import CustomUser

class PasswordReset(models.Model):
    reset_id = models.UUIDField(
        unique=True, 
        default=uuid.uuid4, 
        editable=False, 
        primary_key=True
    )
    used = models.BooleanField(default=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )

class Meta:
    verbose_name = "Password reset ID"
    verbose_name_plural = "Password reset IDs"