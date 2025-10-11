from django.db import models
from django.utils import timezone
from core.models import CustomUser
import zoneinfo


class CalendarEntry(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.DateTimeField(
        default=timezone.now,
        blank=False,
        null=False
    )
    title = models.CharField(
        max_length=1000,
        null=False,
        blank=False)
    description = models.CharField(
        max_length=1000,
        null=True,
        blank=True)
    custom_user_id = models.ForeignKey(  # The author of the message
        CustomUser,
        on_delete=models.CASCADE,
        related_name="custom_user_calendar_entries"
    )
    created_on = models.DateTimeField(
        default=timezone.now,
        editable=False
    )

    def serialized(self):
        return {
            'ID': self.id, 'date': self.date.astimezone(zoneinfo.ZoneInfo("Europe/Paris")),
            'title': self.title, 'description': self.description, 'type': '',
        }

    class Meta:
        verbose_name = "Calendar Entry"
        verbose_name_plural = "Calendar Entries"
