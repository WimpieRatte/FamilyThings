from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from .models.accomplishment import Accomplishment
from .models.family_user_accomplishment import FamilyUserAccomplishment
from .forms.accomplishment import AccomplishmentForm
from core.models.family import Family
from core.models.family_user import FamilyUser
from core.models.custom_user import CustomUser
from core.session import create_alert, get_locale_text
from django.utils import timezone
import uuid


def get_obtained_today(request, amount: int = 4):
    """Obtain a JSON with a user's Accomplishments they obtained today"""
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    else:
        today: timezone.datetime = timezone.now()
        return JsonResponse(data={
            'result': list(reversed(Accomplishment.objects.filter(
                created_by=request.user.id,
                created__year=today.year,
                created__month=today.month,
                created__day=today.day).order_by('created').values()[:amount]))
        })


def get_recent(request, amount: int = 5):
    """Obtain a JSON with a user's recent Accomplishments"""
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    else:
        return JsonResponse(data={
            'result': list(reversed(Accomplishment.objects.filter(
                    created_by=request.user.id).order_by('created').values()[:amount]))
        })


def submit_accomplishment(request):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest(
            get_locale_text(
                request=request, ID="login-required",
                text="For this action, you need to login first."))

    family_user: FamilyUser = FamilyUser.objects.get(custom_user_id=request.user)
    if family_user == None:
        return HttpResponseBadRequest(
            get_locale_text(
                request=request, ID="not-in-a-family",
                default_text="You aren't part of a Family."))

    print(request.POST)

    form = AccomplishmentForm(data=request.POST)
    if form.is_valid():
        new_acc, created = Accomplishment.objects.get_or_create(
            created_by=request.user,
            name=form.cleaned_data.get("name"),
            description=form.cleaned_data.get("description", ""),
            icon=form.cleaned_data.get("icon", "")
        )
        FamilyUserAccomplishment.objects.get_or_create(
            family_user_id=family_user,
            accomplishment_id=new_acc,
            created_by=request.user,
            measurement_quantity=form.cleaned_data.get("measurement_quantity", 1),
            from_date=timezone.now(),
            to_date=timezone.now()
        )
        return JsonResponse({})
    else:
        print(form.errors)

    return HttpResponseBadRequest(
        get_locale_text(
            request=request, ID="accomplishment-create-failed",
            default_text="Accomplishment couldn't be submitted."))
