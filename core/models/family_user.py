import uuid
from django.db import models

from .family import Family
from .custom_user import CustomUser


class FamilyUser(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    family_id = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="family"
    )
    custom_user_id = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="custom_user"
    )
    join_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Family User"
        verbose_name_plural = "Family Users"
