import uuid
from django.db import models
from .custom_user import CustomUser
from core.utils import get_first_custom_user

class Family(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    created_by = models.ForeignKey(
        CustomUser,
        default=get_first_custom_user,
        on_delete=models.CASCADE,
        related_name="family_createdcustom_user"
    )

    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"
