import uuid
from django.db import models
from django.utils import timezone
from core.models import Family


class FamilyChat(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    family_id = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        editable=False,
        related_name="family_family_chats",
    )
    created_on = models.DateTimeField(
        default=timezone.now,
        editable=False
    )

    def __str__(self):
        return f"{self.family_id.name[:9]}~Chat: {self.id}"

    class Meta:
        verbose_name = "Family Chat"
        verbose_name_plural = "Family Chats"
