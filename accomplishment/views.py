import zoneinfo
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Accomplishment, FamilyUserAccomplishment, AccomplishmentType
from .forms.accomplishment import AccomplishmentForm
from . import constants
from core.views import render_if_logged_in
from core.session import update_session, create_alert, get_locale_text
from core.models.custom_user import CustomUser


def page_overview(request, lang_code: str = ""):
    """An overview of an User's Accomplishments."""
    update_session(request=request, lang_code=lang_code)

    if not request.user.is_authenticated:
        create_alert(request=request, ID="login-required", type="warning",
            text="For this action, you need to login first.")
        return redirect("core:user_login")

    recent_additions = Accomplishment.objects.filter(
                    created_by=request.user.id).order_by('created').values()[:10]

    target: HttpResponse = render(
        request, "accomplishment/accomp_overview.html",
        {
            'recent_additions': list(reversed(Accomplishment.objects.filter(id__in=recent_additions))),
            'colors': ['red', 'blue', 'green', 'orange', 'purple', 'cyan']
        })

    return render_if_logged_in(request, target)


def page_new_accomplishment(request, lang_code: str = "", ID: int = -1):
    """."""
    update_session(request=request, lang_code=lang_code,
                   cache_last_visited_page=False)

    form: AccomplishmentForm = AccomplishmentForm()

    if ID != -1:
        accom: Accomplishment = Accomplishment.objects.get(id=ID)
        form = AccomplishmentForm(initial={
            'name': accom.name,
            'description': accom.description,
            'icon': accom.icon,
            'is_achievement': accom.is_achievement
        })

    return render(
        request, "accomplishment/accomp_add_new.html",
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


def page_edit_user_accomplishment(request, lang_code: str = "", ID: int = -1):
    """."""
    update_session(request=request, lang_code=lang_code,
                   cache_last_visited_page=False)

    form: AccomplishmentForm = AccomplishmentForm()

    if ID != -1:
        accom: FamilyUserAccomplishment = FamilyUserAccomplishment.objects.get(id=ID)

        if (request.POST):
            form = AccomplishmentForm(data=request.POST)
            print(form.data)
            if (request.POST["measurement"]):
                accom.accomplishment_id.measurement_type_id = form.data.get(
                    "measurement", accom.accomplishment_id.measurement_type_id)

            accom.measurement_quantity = request.POST["measurement_quantity"]
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
            request, "accomplishment/accomp_edit_milestone.html", {"form": form})


def page_edit_accomplishment_details(request, lang_code: str = "", ID: int = -1):
    """."""
    update_session(request=request, lang_code=lang_code,
                   cache_last_visited_page=False)

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
            accom_details.save()
            return redirect("accomplishment:overview")

        accomp_data: dict = {
            'name': accom_details.name, 'description': accom_details.description,
            'icon': accom_details.icon
        }

        # Apply the name of the AccomplishmentType if it was defined
        if accom_details.accomplishment_type_id:
            accomp_data["accomplishment_type"] = accom_details.accomplishment_type_id.name

        form = AccomplishmentForm(data=accomp_data)

        return render(
            request, "accomplishment/accomp_edit_details.html", {
                "form": form, "icons": constants.ICONS,
                "initial": accomp_data})
