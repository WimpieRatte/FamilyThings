from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    BLUE = "blue"
    INDIGO = "indigo"
    PURPLE = "purple"
    PINK = "pink"
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    TEAL = "teal"
    CYAN = "cyan"
    COLOR_CHOICES = {
        BLUE: "Blue",
        INDIGO: "Indigo",
        PURPLE: "Purple",
        PINK: "Pink",
        RED: "Red",
        ORANGE: "Orange",
        YELLOW: "Yellow",
        GREEN: "Green",
        TEAL: "Teal",
        CYAN: "Cyan"
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
    last_name = None
    is_manager = models.BooleanField(
        default=False
    )
    first_name = models.CharField(max_length=20)
    birthday = models.DateField(blank=True, null=True)
    color = models.CharField(
        max_length=6,
        choices=COLOR_CHOICES,
        default=BLUE)
    icon = models.ImageField(upload_to="icons",
                             blank=True, null=True)
    background_image = models.ImageField(upload_to="backgrounds/",
                                         blank=True, null=True)

    def __str__(self):
        return f"user {self.username}"

    class Meta:
        # White space as workaround for the ordering.
        verbose_name = "  User"
        verbose_name_plural = "  Users"
