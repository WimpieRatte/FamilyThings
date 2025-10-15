from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone

from core.models.family_user import FamilyUser
from ft_calendar.forms.calender_event import CalendarEventForm
from .models import CalendarEntry
from core.session import update_user_session, create_alert, get_locale_text, JsonResponseAlert


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

@update_user_session()
def create_calendar_entry(request):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest(
            get_locale_text(
                request=request, ID="login-required",
                default_text="For this action, you need to login first."
            )
        )

    try:
        family_user: FamilyUser = FamilyUser.objects.filter(
            custom_user_id=request.user
        )[request.session["current_family"]]
    except (FamilyUser.DoesNotExist, IndexError, KeyError):
        return HttpResponseBadRequest(
            get_locale_text(
                request=request, ID="not-in-a-family",
                default_text="You aren't part of a Family."
            )
        )

    form = CalendarEventForm(data=request.POST)
    if form.is_valid():
        print(form.cleaned_data)

        # Create or fetch calendar entry uniquely by family + user + title + date
        new_calendar_entry, created = CalendarEntry.objects.get_or_create(
            family_id=family_user.family_id,
            custom_user_id=request.user,
            title=form.cleaned_data.get("title"),
            date=form.cleaned_data.get("date"),
            defaults={
                "description": form.cleaned_data.get("description", ""),
                "created_on": timezone.now(),
            }
        )

        # If the entry already existed, update description if needed
        if not created:
            new_calendar_entry.description = form.cleaned_data.get("description", "")
            new_calendar_entry.save()

        return JsonResponseAlert(
            request=request,
            message="Calendar entry successfully created!",
            type="success"
        )
    else:
        print(form.errors)

    return HttpResponseBadRequest(
        get_locale_text(
            request=request, ID="calendar-entry-create-failed",
            default_text="Calendar entry couldn't be submitted."
        )
    )


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
