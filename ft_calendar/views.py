import zoneinfo
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import CalendarEntry
from core.views import render_if_logged_in
from core.session import update_user_session, create_alert, get_locale_text
from core.models.custom_user import CustomUser


@update_user_session()
def page_calendar(request, lang_code: str = ""):
    """."""
    if not request.user.is_authenticated:
        create_alert(request=request, ID="login-required", type="warning",
            text="For this action, you need to login first.")
        return redirect("core:user_login")

    target: HttpResponse = render(
        request, "calendar.html",
        {
            'entries': list(CalendarEntry.objects.filter(
                custom_user_id=request.user
            ).values())
        })

    return render_if_logged_in(request, target)


def get(request, lang_code: str = ""):
    """."""
    query = CalendarEntry.objects.filter(custom_user_id=request.user)

    entries: list = []
    for entry in query:
        entries += [entry.serialized()]

    # Add own birthday
    if (request.user.birthday):
        birthday = request.user.birthday
        next_birthday = timezone.datetime(year=timezone.datetime.now().year, month=birthday.month, day=birthday.day)
        age: int = next_birthday.year - birthday.year
        entries += [{
            'ID': -100, 'title': f'Your {age}th Birthday',
            'date': timezone.datetime(year=timezone.datetime.now().year, month=birthday.month, day=birthday.day),
            'icon': 'cake', 'type': 'birthday', 'description': 'Make sure to celebrate it plenty!'}]

    return JsonResponse({
        'entries': entries
    })
