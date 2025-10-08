import uuid
from django.db import models
from .family import Family
from .custom_user import CustomUser


class FamilyInvite(models.Model):
    id = models.BigIntegerField(primary_key=True)
    family_id = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="family_invites"
    )
    generated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="custom_user_generated_family_invites"
    )
    token = models.CharField(max_length=1000)
    created = models.DateTimeField(
        auto_now_add=True
    )
    expiry_date = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Family Invite"
        verbose_name_plural = "Family Invites"
