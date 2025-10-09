import json
import zoneinfo
from django.http import JsonResponse, HttpResponseBadRequest, Http404
from django.utils import timezone
from django.core.serializers import serialize
from .models import Accomplishment, FamilyUserAccomplishment, AccomplishmentType, MeasurementType
from .forms.accomplishment import AccomplishmentForm
from core.models.family import Family
from core.models.family_user import FamilyUser
from core.models.custom_user import CustomUser
from core.session import get_locale_text, JsonResponseAlert


def accomplishments_list_from_query(query):
    """Return a list of Accomplishments based on a
    FamilyUserAccomplishment QuerySet."""
    result = []
    for _ in query:
        _ = Accomplishment.objects.filter(id__in=_).values()
        result += _
    result = list(result)

    return (result)


def get_obtained_today(request, amount: int = 4):
    """Obtain a JSON with a user's Accomplishments they obtained today"""
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    else:
        today: timezone.datetime = timezone.now()
        fam_user_accomplishments = FamilyUserAccomplishment.objects.filter(
                created_by_id=request.user,
                created__year=today.year,
                created__month=today.month,
                created__day=today.day
        ).order_by('created').reverse().values_list("accomplishment_id")[:amount]

        return JsonResponse(data={
            'result': accomplishments_list_from_query(fam_user_accomplishments)
        })


def get_recent(request, amount: int = 5):
    """Obtain a JSON with a user's recent Accomplishments"""
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    else:
        yesterday: timezone.datetime = timezone.now() - timezone.timedelta(days=1)
        fam_user_accomplishments = FamilyUserAccomplishment.objects.filter(
                created_by_id=request.user,
                created__lt=yesterday
        ).order_by('created').reverse().values_list("accomplishment_id")[:amount]

        return JsonResponse(data={
            'result': accomplishments_list_from_query(fam_user_accomplishments)
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
        output[i]["fields"]['accomplishment'] = entry.accomplishment_id.dict()

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
        result: Accomplishment = Accomplishment.objects.get(name=name)
        return JsonResponse(
            data={
                'name': result.name,
                'description': result.description,
                'icon': result.icon
                })
    except (Accomplishment.DoesNotExist):
        return Http404


def get_milestone_by_id(request, ID):
    accom: FamilyUserAccomplishment = FamilyUserAccomplishment.objects.get(
        id=ID, family_user_id__custom_user_id=request.user)

    from_date_tz = accom.from_date.astimezone(zoneinfo.ZoneInfo("Europe/Paris"))
    to_date_tz = accom.to_date.astimezone(zoneinfo.ZoneInfo("Europe/Paris"))

    accom_details = accom.accomplishment_id.dict()
    return JsonResponse(data={
        'measurement': accom_details['measurement'],
        'measurement_quantity': accom.measurement_quantity,
        'date_from_day': from_date_tz.day, 'date_from_month': from_date_tz.month,
        'date_from_year': from_date_tz.year, 'date_to_day': to_date_tz.day,
        'date_to_month': to_date_tz.month, 'date_to_year': to_date_tz.year,
    })


def edit_milestone(request, ID):
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

        accom.from_date = datetime_from_field(form=form, field="date_from")
        accom.to_date = datetime_from_field(form=form, field="date_to")
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
        print(form.cleaned_data)
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
                    name=form.cleaned_data.get("accomplishment_type", ""),
                    description=""
                )[0]
                new_accomp.accomplishment_type_id = accomp_type

            if form.cleaned_data.get("measurement", "") != "":
                measurement: MeasurementType = MeasurementType.objects.get_or_create(
                    name=form.cleaned_data.get("measurement", ""),
                    abbreviation=form.cleaned_data.get("measurement", ""),
                    description=""
                )[0]
                new_accomp.measurement_type_id = measurement

            new_accomp.description=form.cleaned_data.get("description", ""),
            new_accomp.icon=form.cleaned_data.get("icon", "")
            new_accomp.is_achievement=form.cleaned_data.get("is_achievement", False)
            new_accomp.save()

        FamilyUserAccomplishment.objects.get_or_create(
            family_user_id=family_user,
            accomplishment_id=new_accomp,
            created_by=request.user,
            measurement_quantity=form.cleaned_data.get("measurement_quantity", 1),
            from_date=timezone.now(),
            to_date=timezone.now()
        )
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
        message: FamilyUserAccomplishment = \
            FamilyUserAccomplishment.objects.get(
                id=ID, created_by=request.user)
        message.delete()
        return JsonResponse(
            data={'alert-message': "", 'alert-type': 'success'})
    except (FamilyUserAccomplishment.DoesNotExist):
        return HttpResponseBadRequest()
