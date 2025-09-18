import uuid
from django.db import models

class CustomUser(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(
         unique=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now_add=True
    )
    last_login = models.DateTimeField(
        auto_now_add=True
    )
    is_super_user = models.BooleanField(
        default=False
    )
    
