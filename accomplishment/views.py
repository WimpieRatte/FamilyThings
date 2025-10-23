import zoneinfo
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Accomplishment, FamilyUserAccomplishment, AccomplishmentType, MeasurementType
from .forms.accomplishment import AccomplishmentForm
from . import constants
from core.session import update_user_session, create_alert, get_locale_text
from core.models.custom_user import CustomUser


@update_user_session()
def page_overview(request, popup: str = ""):
    """An overview of an User's Accomplishments."""

    recent_additions = Accomplishment.objects.filter(
                    created_by=request.user.id).order_by('-created').values()[:15]

    return render(
        request, "accomp_overview.html",
        {
            'recent_additions': list(reversed(Accomplishment.objects.filter(id__in=recent_additions))),
            'colors': ['red', 'blue', 'green', 'orange', 'purple', 'cyan'],
            'icons': constants.ICONS,
            'categories': constants.CATEGORIES,
            'measurements': constants.MEASUREMENTS,
            'form': AccomplishmentForm(),
            'popup': popup
        })


@update_user_session()
def page_new_accomplishment(request, ID: int = -1, name: str = ""):
    """."""
    form: AccomplishmentForm = AccomplishmentForm()

    if name != "":
        form = AccomplishmentForm(initial={'name': name})

    if ID != -1:
        accom: Accomplishment = Accomplishment.objects.get(id=ID)
        form = AccomplishmentForm(initial={
            'name': accom.name,
            'description': accom.description,
            'icon': accom.icon,
            'is_achievement': accom.is_achievement,
            'measurement': accom.measurement_type_id.abbreviation
        })

    return render(
        request, "accomp_add_new.html",
        {
            "form": form,
            "icons": constants.ICONS,
            "initial": form.initial
        })


def datetime_from_field(form: AccomplishmentForm, field: str = "",
                        tz: str = "Europe/Paris"):
    return timezone.datetime(
        year=int(form.data[field+"_year"]),
        month=int(form.data[field+"_month"]),
        day=int(form.data[field+"_day"]),
        tzinfo=zoneinfo.ZoneInfo(tz))


@update_user_session()
def page_edit_user_accomplishment(request, ID: int = -1, cache_last_visited_page=False):
    """."""
    form: AccomplishmentForm = AccomplishmentForm()

    if ID != -1:
        accom: FamilyUserAccomplishment = FamilyUserAccomplishment.objects.get(id=ID)

        if (request.POST):
            form = AccomplishmentForm(data=request.POST)

            if (request.POST["measurement_quantity"] == ""):
                accom.measurement_quantity = 0
            else:
                accom.measurement_quantity = int(request.POST.get("measurement_quantity", 0))

            accom.from_date = datetime_from_field(form=form, field="date_from")
            accom.to_date = datetime_from_field(form=form, field="date_to")
            accom.save()

            return redirect("accomplishment:overview")

        form = AccomplishmentForm(data={
            'measurement': accom.accomplishment_id.measurement_type_id,
            'measurement_quantity': accom.measurement_quantity,
            'date_from': accom.from_date.astimezone(zoneinfo.ZoneInfo("Europe/Paris")),
            'date_to': accom.to_date.astimezone(zoneinfo.ZoneInfo("Europe/Paris")),
        })

        return render(
            request, "accomp_edit_milestone.html", {"form": form})


@update_user_session()
def page_edit_accomplishment_details(request, ID=-1):
    """."""
    form: AccomplishmentForm = AccomplishmentForm()
    if ID != -1:
        accom_details: Accomplishment = FamilyUserAccomplishment.objects.get(
            id=ID).accomplishment_id

        if (request.POST):
            form = AccomplishmentForm(data=request.POST)
            accom_details.name = request.POST["name"]
            accom_details.description = request.POST["description"]
            accom_details.icon = request.POST["icon"]
            if request.POST.get("accomplishment_type", "") != "":
                accom_details.accomplishment_type_id = AccomplishmentType.objects.get_or_create(
                        name=request.POST["accomplishment_type"])[0]
            if request.POST.get("measurement", "") != "":
                accom_details.measurement_type_id = MeasurementType.objects.get_or_create(
                        abbreviation=request.POST["measurement"])[0]
            accom_details.save()
            return redirect("accomplishment:overview")

        accomp_data = accom_details.serialized()

        form = AccomplishmentForm(data=accomp_data)

        return render(
            request, "accomp_edit_details.html", {
                "form": form, "icons": constants.ICONS,
                "initial": accomp_data})
