import uuid
from django.db import models
from django.utils import timezone
from . import FamilyChat
from core.models import CustomUser


class Message(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    text = models.CharField(max_length=1000)
    custom_user_id = models.ForeignKey(  # The author of the message
        CustomUser,
        on_delete=models.CASCADE,
        related_name="custom_user_messages"
    )
    family_chat_id = models.ForeignKey(  # The FamilyChat this message belongs to
        FamilyChat,
        on_delete=models.CASCADE,
        related_name="family_chat_messages"
    )
    created_on = models.DateTimeField(
        default=timezone.now
    )
    deleted = models.BooleanField(
        default=False
    )
    deleted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name="deleted_by_user_messages",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.custom_user_id.username[:7]}~Fam: {self.family_chat_id.family_id.name[:9]}~{self.text[:4]}"

    def content(self):
        if not self.deleted:
            return self.text
        else:
            return "<i>(Message deleted.)</i>"

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
