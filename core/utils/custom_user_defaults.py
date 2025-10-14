from core.models import CustomUser

def get_first_custom_user():
    """Return the first available CustomUser's ID in the database or ``None`` if no users exist."""
    try:
        return CustomUser.objects.order_by("id").first().id
    except AttributeError:
        return None
    except CustomUser.DoesNotExist:
        return None
