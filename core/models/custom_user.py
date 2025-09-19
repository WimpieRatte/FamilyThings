from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    RED = "RD"
    BLUE = "BL"
    L_BLUE = "LBL"
    PINK = "PNK"
    COLOR_CHOICES = {
        RED: "Red",
        BLUE: "Blue",
        L_BLUE: "Light Blue",
        PINK: "Pink"
    }
    email = models.EmailField(
         unique=True
    )
    created = models.DateTimeField(
        default=timezone.now
    )
    updated = models.DateTimeField(
        default=timezone.now
    )
    last_login = models.DateTimeField(
        default=timezone.now
    )
    is_super_user = models.BooleanField(
        default=False
    )
    is_manager = models.BooleanField(
        default=False
    )
    first_name = models.CharField(max_length=20)
    birthday = models.DateField(blank=True, null=True)
    color = models.CharField(
        max_length=4,
        choices=COLOR_CHOICES,
        default=BLUE)
    picture = models.ImageField(upload_to="uploads/", blank=True, null=True)

    def __str__(self):
        return f"user {self.username}"
