from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from ..constants import COLORS, LANGUAGES


class CustomUser(AbstractUser):
    """The default User class of FamilyThings."""
    # Overriding Django's built-in AbstractUser
    email = models.EmailField(unique=True)

    # TODO: Check if 'created' is required
    # Django has 'date_joined' built-in, which has the same function
    # created = models.DateTimeField(default=timezone.now)

    # Login/Settings tracking
    updated = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(default=timezone.now)

    # Used to define an User as Family Manager

    # Personalization-related fields
    first_name = models.CharField(max_length=20, default="")
    last_name = models.CharField(max_length=20, default="")
    birthday = models.DateField(blank=True, null=True)
    color = models.CharField(
        max_length=6,
        choices=COLORS,
        default="blue")
    icon = models.ImageField(
        blank=True, null=True,
        upload_to="icons/")
    background_image = models.ImageField(
        blank=True, null=True,
        upload_to="backgrounds/")
    # Misc. settings
    lang_code = models.CharField(
        max_length=3,
        choices=LANGUAGES,
        default="")
    cursor = models.BooleanField(
        default=True
    )

    def __str__(self):
        """Return the Username as the model's default string representation."""
        return self.username

    def full_name(self):
        """Return either the Username or, if defined, the First and Last Names."""
        if self.first_name != "":
            return f"{self.first_name} {self.last_name}".replace(" None", "")
        return self.username

    class Meta:
        # White space is used as a workaround
        # for the ordering in the Admin page.
        verbose_name = "  User"
        verbose_name_plural = "  Users"
