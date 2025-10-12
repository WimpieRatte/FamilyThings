import random
import string
from django.db import models
from .family import Family
from .custom_user import CustomUser


class FamilyInvite(models.Model):
    id = models.BigAutoField(primary_key=True)
    family_id = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="family_invites"
    )
    generated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="custom_user_generated_family_invites"
    )
    token = models.CharField(
        max_length=1000,
        null=False,
        blank=False,
        default=''.join(random.choices(string.ascii_letters + string.digits, k=40))
    )
    created = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    expiry_date = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Family Invite"
        verbose_name_plural = "Family Invites"
