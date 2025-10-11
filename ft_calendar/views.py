import zoneinfo
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import CalendarEntry
from core.views import render_if_logged_in
from core.session import update_session, create_alert, get_locale_text
from core.models.custom_user import CustomUser


def page_calendar(request, lang_code: str = ""):
    """An overview of an User's Accomplishments."""
    update_session(request=request, lang_code=lang_code)

    if not request.user.is_authenticated:
        create_alert(request=request, ID="login-required", type="warning",
            text="For this action, you need to login first.")
        return redirect("core:user_login")

    target: HttpResponse = render(
        request, "calendar.html",
        {
            'entries': list(CalendarEntry.objects.filter(
                custom_user_id=request.user
            ).values_list())
        })

    return render_if_logged_in(request, target)