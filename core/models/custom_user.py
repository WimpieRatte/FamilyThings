from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """The default User class of FamilyThings."""
    # Color constants; used as the site's primary color.
    # The associated field can be found under 'Personalization-related fields'
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
        BLUE: "Blue", INDIGO: "Indigo", PURPLE: "Purple",
        PINK: "Pink", RED: "Red", ORANGE: "Orange",
        YELLOW: "Yellow", GREEN: "Green", TEAL: "Teal", CYAN: "Cyan"
    }

    ENGLISH = "en"
    GERMAN = "de"
    LANG_CHOICES = {
        ENGLISH: "English", GERMAN: "German"
    }

    # Overriding Django's built-in AbstractUser
    email = models.EmailField(unique=True)
    last_name = models.CharField(max_length=20, null=True)  # Overwritten to be removed, as it's not required.

    # TODO: Check if 'created' is required
    # Django has 'date_joined' built-in, which has the same function
    # created = models.DateTimeField(default=timezone.now)

    # Login/Settings tracking
    updated = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(default=timezone.now)

    # Used to define an User as Family Manager
    is_manager = models.BooleanField(default=False)

    # Personalization-related fields
    first_name = models.CharField(max_length=20)
    birthday = models.DateField(blank=True, null=True)
    color = models.CharField(
        max_length=6,
        choices=COLOR_CHOICES,
        default=BLUE)
    icon = models.ImageField(
        blank=True, null=True,
        upload_to="icons")
    background_image = models.ImageField(
        blank=True, null=True,
        upload_to="backgrounds/")

    # Misc. settings
    lang_code = models.CharField(
        max_length=3,
        choices=LANG_CHOICES,
        default="")
    cursor = models.BooleanField(
        default=True
    )

    def __str__(self):
        """Return the Username as the model's default string representation."""
        return self.username

    class Meta:
        # White space is used as a workaround
        # for the ordering in the Admin page.
        verbose_name = "  User"
        verbose_name_plural = "  Users"
