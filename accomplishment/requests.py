import json
from django.http import JsonResponse, HttpResponseBadRequest, Http404
from django.utils import timezone
from django.core.serializers import serialize
from .models.accomplishment import Accomplishment
from .models.family_user_accomplishment import FamilyUserAccomplishment
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


def get_entities(request, amount: int = 5, start: int = 0, key=""):
    """."""
    start = max(int(start)-1, 0)

    if not request.user.is_authenticated:
        return HttpResponseBadRequest()

    total_accomplishments = FamilyUserAccomplishment.objects.filter(
            created_by_id=request.user,
            accomplishment_id__name__icontains=key)
    output = FamilyUserAccomplishment.objects.filter(
            created_by_id=request.user,
            accomplishment_id__name__icontains=key).order_by(
                'created').reverse()[start:start+int(amount)]

    cache = output
    output = json.loads(serialize("json", list(output)))

    for i, entry in enumerate(cache):
        output[i]["fields"]['accomplishment'] = entry.accomplishment_id.dict()

    count = cache.count()

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


def submit_accomplishment(request):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest(
            get_locale_text(
                request=request, ID="login-required",
                text="For this action, you need to login first."))

    family_user: FamilyUser = FamilyUser.objects.filter(custom_user_id=request.user)[request.session["current_family"]]
    if family_user is None:
        return HttpResponseBadRequest(
            get_locale_text(
                request=request, ID="not-in-a-family",
                default_text="You aren't part of a Family."))

    form = AccomplishmentForm(data=request.POST)
    if form.is_valid():
        new_acc, created = Accomplishment.objects.get_or_create(
            created_by=request.user,
            name=form.cleaned_data.get("name"),
        )
        if created:
            print("New Accomplishment")
            new_acc.description=form.cleaned_data.get("description", ""),
            new_acc.icon=form.cleaned_data.get("icon", "")
            new_acc.save()
        FamilyUserAccomplishment.objects.get_or_create(
            family_user_id=family_user,
            accomplishment_id=new_acc,
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
