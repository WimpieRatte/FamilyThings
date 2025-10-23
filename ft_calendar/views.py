from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from core.models.family_user import FamilyUser
from ft_calendar.forms.calender_event import CalendarEventForm
from .models import CalendarEntry
from core.session import update_user_session, create_alert, get_locale_text, JsonResponseAlert


@update_user_session()
def page_calendar(request, start: int = timezone.now().day):
    """Return the Calendar overview page."""
    return render(
        request, "calendar.html",
        {
            'entries': list(CalendarEntry.objects.filter(
                custom_user_id=request.user
            ).values()),
            'day': start
        })

@update_user_session()
def create_or_edit_calendar_entry(request, event_id=None):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest("You must be logged in.")

    try:
        family_user: FamilyUser = FamilyUser.objects.filter(
            custom_user_id=request.user
        )[request.session["current_family"]]
    except (FamilyUser.DoesNotExist, IndexError, KeyError):
        return HttpResponseBadRequest("You aren't part of a family.")

    form = CalendarEventForm(data=request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid form data.")

    if event_id:
        # ✏️ Editing an existing entry
        calendar_entry = get_object_or_404(CalendarEntry, id=event_id, custom_user_id=request.user.id)
        calendar_entry.title = form.cleaned_data["title"]
        calendar_entry.description = form.cleaned_data.get("description", "")
        calendar_entry.date = form.cleaned_data["date"]
        calendar_entry.save()
        return JsonResponse({"status": "success", "message": "Event updated successfully!"})

    # 🆕 Creating a new entry
    CalendarEntry.objects.create(
        family_id=family_user.family_id,
        custom_user_id=request.user,
        title=form.cleaned_data["title"],
        description=form.cleaned_data.get("description", ""),
        date=form.cleaned_data["date"],
        created_on=timezone.now(),
    )
    return JsonResponse({"status": "success", "message": "Event created successfully!"})

@update_user_session()
def delete_calendar_entry(request, event_id):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method.")

    try:
        # Ensure the user owns this event
        event = CalendarEntry.objects.get(id=event_id, custom_user_id=request.user)
        event.delete()
        return JsonResponse({
            "status": "success",
            "message": "Calendar entry deleted successfully!"
        })
    except CalendarEntry.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Event not found or you don't have permission to delete it."
        }, status=404)


def get(request):
    """Return all CalendarEntries tied to a User."""
    query = CalendarEntry.objects.filter(custom_user_id=request.user).order_by("created_on")

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
