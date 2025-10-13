import uuid
from django.db import models
from django.utils import timezone

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
        related_name="family_family_users"
    )
    custom_user_id = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="custom_user_family_users"
    )
    join_date = models.DateTimeField(
        default=timezone.now
    )
    is_manager = models.BooleanField(default=False)

    def serialized(self):
        """Return a JSONSerializable representation of the FamilyUser."""
        return {'family_ID': str(self.family_id.id), 'family_name': self.family_id.name,
                'ID': str(self.custom_user_id.id),'is_manager': self.is_manager,
                'username': self.custom_user_id.username, 'full_name': self.custom_user_id.full_name(),
                'joined': self.join_date.strftime("%Y/%m/%d"), 'icon': self.custom_user_id.icon.name, 'color': self.custom_user_id.color}

    class Meta:
        verbose_name = "Family User"
        verbose_name_plural = "Family Users"
