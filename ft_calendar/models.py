from django.db import models
from django.utils import timezone
from core.models import CustomUser, Family
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
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="custom_user_calendar_entries"
    )
    family_id = models.ForeignKey(  # The author of the message
        Family,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="family_calendar_entries"
    )
    created_on = models.DateTimeField(
        default=timezone.now,
        editable=False
    )

    def serialized(self):
        output: dict = {
            'ID': self.id, 'date': self.date.astimezone(zoneinfo.ZoneInfo("Europe/Paris")),
            'title': self.title, 'description': self.description, 'type': '',
            'family': "N/A"
        }

        if self.family_id:
            output['family'] = self.family_id.name
        return {
            'ID': self.id, 'date': self.date.astimezone(zoneinfo.ZoneInfo("Europe/Paris")),
            'title': self.title, 'description': self.description, 'type': '',
        }

    class Meta:
        verbose_name = "Calendar Entry"
        verbose_name_plural = "Calendar Entries"
