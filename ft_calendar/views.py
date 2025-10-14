import zoneinfo
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import CalendarEntry
from core.views import render_if_logged_in
from core.session import update_user_session, create_alert, get_locale_text
from core.models.custom_user import CustomUser


@update_user_session()
def page_calendar(request, start: int = timezone.now().day):
    """Return the Calendar overview page."""
    print(start)
    return render(
        request, "calendar.html",
        {
            'entries': list(CalendarEntry.objects.filter(
                custom_user_id=request.user
            ).values()),
            'day': start
        })


def get(request):
    """Return all CalendarEntries tied to a User."""
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
