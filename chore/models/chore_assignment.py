from django.db import models
from core.models import FamilyUser, Status
from .chore import Chore


class ChoreAssignment(models.Model):
    id = models.BigIntegerField(
        primary_key=True,
        unique=True
        )
    chore_id = models.ForeignKey(
        Chore,
        on_delete=models.CASCADE,
        related_name='chore_assignments'
    )
    assigned_to = models.ForeignKey(
        FamilyUser,
        on_delete=models.CASCADE,
        related_name="family_user_chores_to_do"
    )
    assigned_by = models.ForeignKey(
        FamilyUser,
        on_delete=models.CASCADE,
        related_name="family_user_chores_assigned_to_others"
    )
    due_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    status_id = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        related_name="status_chore_assignments"
    )

    class Meta:
        verbose_name = "Chore Assignment"
        verbose_name_plural = "Chore Assignments"
