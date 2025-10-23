import json
import zoneinfo
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import Accomplishment, FamilyUserAccomplishment, AccomplishmentType, MeasurementType
from .forms.accomplishment import AccomplishmentForm
from core.models.family import Family
from core.models.family_user import FamilyUser
from core.models.custom_user import CustomUser
from core.session import get_locale_text, JsonResponseAlert
from django.shortcuts import render, redirect


def accomplishments_list_from_query(query):
    """Return a list of Accomplishments based on a
    FamilyUserAccomplishment QuerySet."""
    result = []
    user_accomp: FamilyUserAccomplishment
    for user_accomp in query:
        result += [user_accomp.serialized()]
    result = list(result)

    return (result)


def get_obtained_today(request, amount: int = 4):
    """Obtain a JSON with a user's Accomplishments they obtained today"""
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    else:
        today: timezone.datetime = timezone.now()
        query = FamilyUserAccomplishment.objects.filter(
                created_by_id=request.user,
                created__year=today.year,
                created__month=today.month,
                created__day=today.day
        ).order_by('created')

        return JsonResponse(data={
            'result': accomplishments_list_from_query(query=query[:min(amount, len(query))])
        })


def get_recent(request, amount: int = 5):
    """Obtain a JSON with a user's recent Accomplishments"""
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    else:
        yesterday: timezone.datetime = timezone.now() - timezone.timedelta(days=1)
        query = FamilyUserAccomplishment.objects.filter(
                created_by_id=request.user,
                created__lt=yesterday
        ).order_by('-created')

        return JsonResponse(data={
            'result': accomplishments_list_from_query(query=query[:min(amount, len(query))])
        })


def get_entries(request, amount: int = 5, start: int = 0, selector: str = "name", key: str = ""):
    """
    Get a list of FamilyUserAccomplishment entries using some filters.

    :param request: The request.
    :param amount: The amount of entries you want to return.
    :param start: The starting offset.
    :param key: Used to filter using this string. Checks if the string is
    contained inside the name of the underlying Accomplishment.
    """
    start = max(int(start)-1, 0)

    if not request.user.is_authenticated:
        return HttpResponseBadRequest()

    total_accomplishments = FamilyUserAccomplishment.objects.filter(
            created_by_id=request.user)

    match selector:
        case "category":
            total_accomplishments = total_accomplishments.filter(
                accomplishment_id__accomplishment_type_id__name__icontains=key)
        case "uncategorized":
            total_accomplishments = total_accomplishments.filter(
                accomplishment_id__name__icontains=key,
                accomplishment_id__accomplishment_type_id__name=None)
        case "achievement":
            total_accomplishments = total_accomplishments.filter(
                accomplishment_id__name__icontains=key,
                accomplishment_id__is_achievement=True)
        case "name":
            total_accomplishments = total_accomplishments.filter(
                accomplishment_id__name__icontains=key)

    count = total_accomplishments.count()
    output = total_accomplishments.order_by(
                'created').reverse()[start:start+int(amount)]
    cache = output
    output = json.loads(serialize("json", list(output)))

    for i, entry in enumerate(cache):
        output[i]["fields"]['accomplishment'] = entry.accomplishment_id.serialized()

    return JsonResponse(
        data={
            'result': output,
            'range': {'start': start + 1, 'end': start + count},
            'total': total_accomplishments.count()
        })


def get_by_name(request, name: str):
    """Return details about an Accomplishment if the name matches,
    otherwise return Http404"""
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()

    try:
        result: Accomplishment = Accomplishment.objects.get(
            created_by=request.user,
            name__iexact=name)
        return JsonResponse(data=result.serialized())
    except (Accomplishment.DoesNotExist):
        return HttpResponseNotFound()


def get_names(request):
    """"""
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()

    try:
        result: Accomplishment = Accomplishment.objects.filter(created_by=request.user).values_list("name")
        return JsonResponse(
            data={'name': list(reversed(result))})
    except (Accomplishment.DoesNotExist):
        return HttpResponseNotFound()


def get_accomp_by_id(request, ID):
    accom: FamilyUserAccomplishment = FamilyUserAccomplishment.objects.get(
        id=ID, family_user_id__custom_user_id=request.user)

    from_date_tz = accom.from_date.astimezone(zoneinfo.ZoneInfo("Europe/Paris"))
    to_date_tz = accom.to_date.astimezone(zoneinfo.ZoneInfo("Europe/Paris"))

    accom_details = accom.accomplishment_id.serialized()
    accom_details.update({
        'created': accom.created,
        'measurement_quantity': accom.measurement_quantity,
        'date_from': accom.from_date.strftime("%Y-%m-%d"), 'date_to': accom.to_date.strftime("%Y-%m-%d")
    })

    return JsonResponse(data=accom_details)


def edit_accomp(request, ID):
    def datetime_from_field(form: AccomplishmentForm, field: str = "",
                            tz: str = "Europe/Paris"):
        return timezone.datetime(
            year=int(form.data[field+"_year"]),
            month=int(form.data[field+"_month"]),
            day=int(form.data[field+"_day"]),
            tzinfo=zoneinfo.ZoneInfo(tz))

    try:
        accom: FamilyUserAccomplishment = FamilyUserAccomplishment.objects.get(
            id=ID, family_user_id__custom_user_id=request.user)

        form = AccomplishmentForm(data=request.POST)

        if (request.POST.get("measurement_quantity", "") == ""):
            accom.measurement_quantity = 0
        else:
            accom.measurement_quantity = float(request.POST.get("measurement_quantity", 0))

        accom.from_date = request.POST["date_from"]
        accom.to_date = request.POST["date_to"]
        accom.save()
        return JsonResponseAlert(
            request=request, type="success", message=get_locale_text(
                request=request, ID="changes-applied",
                default_text="All changes have been successfully applied."))
    except (FamilyUserAccomplishment.DoesNotExist):
        return HttpResponseBadRequest()


def submit_accomplishment(request):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest(
            get_locale_text(
                request=request, ID="login-required",
                default_text="For this action, you need to login first."))

    family_user: FamilyUser = FamilyUser.objects.filter(custom_user_id=request.user)[request.session["current_family"]]
    if family_user is None:
        return HttpResponseBadRequest(
            get_locale_text(
                request=request, ID="not-in-a-family",
                default_text="You aren't part of a Family."))

    form = AccomplishmentForm(data=request.POST)
    if form.is_valid():
        # We want to be strict with the name matching, so we only
        # search an Accomplishment with the same name and user,
        # and otherwise create a new one.
        new_accomp, created = Accomplishment.objects.get_or_create(
            created_by=request.user,
            name=form.cleaned_data.get("name"),
        )

        # If it was new, now apply the rest of the new information.
        if created:
            if form.cleaned_data.get("accomplishment_type", "") != "":
                accomp_type = AccomplishmentType.objects.get_or_create(
                    name=form.cleaned_data["accomplishment_type"],
                    description=""
                )[0]
                new_accomp.accomplishment_type_id = accomp_type

            if form.cleaned_data.get("measurement", "") != "":
                measurement: MeasurementType = MeasurementType.objects.get_or_create(
                    name=form.cleaned_data["measurement"],
                    abbreviation=form.cleaned_data["measurement"],
                    description=""
                )[0]
                new_accomp.measurement_type_id = measurement

            if form.cleaned_data.get("description", "") != "":
                new_accomp.description = form.cleaned_data["description"]

            new_accomp.icon=form.cleaned_data.get("icon", "dash")
            new_accomp.is_achievement=form.cleaned_data.get("is_achievement", False)
            new_accomp.save()

        user_accomp, created = FamilyUserAccomplishment.objects.get_or_create(
            family_user_id=family_user,
            accomplishment_id=new_accomp,
            created_by=request.user,
            measurement_quantity=form.cleaned_data.get("measurement_quantity", 1),
        )
        print(form.cleaned_data)
        if form.cleaned_data.get("date", None) is None:
            user_accomp.from_date = form.cleaned_data["date_from"]
            user_accomp.to_date = form.cleaned_data["date_to"]
            user_accomp.save()
        else:
            user_accomp.from_date = form.cleaned_data["date"]
            user_accomp.to_date = form.cleaned_data["date"]
            user_accomp.save()

        return JsonResponseAlert(
            request=request, message="Accomplishment successfully created!",
            type="success")
    else:
        print(form.errors)

    return HttpResponseBadRequest(
        get_locale_text(
            request=request, ID="accomplishment-create-failed",
            default_text="Accomplishment couldn't be submitted."))


def delete_accomplishment(request, ID):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest(get_locale_text(
            request=request, ID="missing-permissions",
            default_text="You don't have permission to perform this operation."))

    try:
        accomp: FamilyUserAccomplishment = \
            FamilyUserAccomplishment.objects.get(
                id=ID, created_by=request.user)
        accomp.delete()

        # Clean up orphaned Accomplishment templates
        template_query = Accomplishment.objects.filter(created_by=request.user)

        for entry in template_query:
            _ = FamilyUserAccomplishment.objects.filter(accomplishment_id=entry)

            if len(_) == 0:
                entry.delete()

        return JsonResponse(
            data={'alert-message': "", 'alert-type': 'success'})
    except (FamilyUserAccomplishment.DoesNotExist):
        return HttpResponseBadRequest()


def require_login(request, func):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest(
            get_locale_text(
                request=request, ID="login-required",
                default_text="For this action, you need to login first."))
    return func



@require_http_methods(["POST"])
def repeat_accomplishment(request):
    try:
        family_user: FamilyUser = FamilyUser.objects.filter(custom_user_id=request.user)[request.session["current_family"]]
        if family_user is None:
            return HttpResponseBadRequest(
                get_locale_text(
                    request=request, ID="not-in-a-family",
                    default_text="You aren't part of a Family."))

        quantity = request.POST.get("measurement_quantity", "")

        if (quantity == ""):
            quantity = 0
        user_accomp = FamilyUserAccomplishment.objects.create(
            family_user_id=family_user,
            accomplishment_id=Accomplishment.objects.get(id=request.POST["ID"]),
            created_by=request.user,
            measurement_quantity=float(quantity),
        )

        if request.POST.get("date", "") == "":
            user_accomp.from_date = request.POST.get("date_from")
            user_accomp.to_date = request.POST.get("date_to")
            user_accomp.save()
        else:
            user_accomp.from_date = request.POST.get("date")
            user_accomp.to_date = request.POST.get("date")
            user_accomp.save()

        return JsonResponseAlert(
            request=request, message="Accomplishment successfully created!",
            type="success")
    except (Exception):
        return HttpResponseBadRequest(
            get_locale_text(
                request=request, ID="accomplishment-create-failed",
                default_text="Accomplishment couldn't be submitted."))


def get_template(request):
    """."""
    ID = request.POST["ID"]
    if ID != -1:
        accom_details: Accomplishment = FamilyUserAccomplishment.objects.get(
            id=ID).accomplishment_id.serialized()

        return JsonResponse(data=accom_details)


def save_template(request):
    """."""
    accom_details: Accomplishment = Accomplishment.objects.get(id=request.POST["ID"])

    form = AccomplishmentForm(data=request.POST)
    if form.is_valid():
        accom_details.name = form.cleaned_data["name"]
        accom_details.description = form.cleaned_data["description"]
        accom_details.icon = form.cleaned_data["icon"]
        if form.cleaned_data.get("is_achievement", "") != "":
            accom_details.is_achievement = form.cleaned_data["is_achievement"]
        if form.cleaned_data.get("accomplishment_type", "") != "":
            accom_details.accomplishment_type_id = AccomplishmentType.objects.get_or_create(
                    name=request.POST["accomplishment_type"])[0]
        if form.cleaned_data.get("measurement", "") != "":
            accom_details.measurement_type_id = MeasurementType.objects.get_or_create(
                    abbreviation=request.POST["measurement"])[0]
        else:
            accom_details.measurement_type_id = None
        accom_details.save()

        return JsonResponseAlert(
                request=request, type="success", message=get_locale_text(
                    request=request, ID="changes-applied",
                    default_text="All changes have been successfully applied."))

    return HttpResponseBadRequest()
