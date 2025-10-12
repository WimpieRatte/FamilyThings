from django.utils.crypto import get_random_string
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone

from core.models import Family, FamilyUser, FamilyInvite
from core.forms import UserFinalizeForm
from core.session import get_locale_text
from accomplishment.models import Accomplishment
from messenger.models import Message, FamilyChat


def create_family(request):
    """"""
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    else:
        form = UserFinalizeForm(data=request.POST)
        if form.is_valid():
            new_name = form.cleaned_data.get("family_name", "")
            if new_name != "":
                new_family = Family.objects.create(
                    name=new_name, created_by=request.user)
                FamilyUser.objects.create(
                    custom_user_id=request.user,
                    family_id=new_family,
                    is_manager=True,
                    join_date=timezone.now())
                FamilyChat.objects.create(family_id=new_family)
                return JsonResponse(data={
                    'alert-message': get_locale_text(
                        request=request, ID="family-create-success",
                        default_text="Welcome to FamilyThings, %PLACEHOLDER%!",
                        insert=request.user.full_name()),
                    'alert-type': 'success'
                    })
        return HttpResponseBadRequest(get_locale_text(
            request=request, ID="family-create-failed",
            default_text="Family couldn't be created."))


def delete_message(request, id):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest(get_locale_text(
            request=request, ID="missing-permissions",
            default_text="You don't have permission to perform this operation."))

    # TODO: Make deletion more secure
    try:
        # Message.objects.get(id=id).delete()
        message: Message = Message.objects.get(id=id)
        message.deleted = True
        message.deleted_by = request.user
        message.save()
        return JsonResponse(
            data={'alert-message': "", 'alert-type': 'success'})
    except (Message.DoesNotExist):
        return HttpResponseBadRequest()


def check_invite(request):
    try:
        invite: FamilyInvite = FamilyInvite.objects.get(token=request.POST["token"])
        return JsonResponse(data={})
    except (FamilyInvite.DoesNotExist):
        return HttpResponseBadRequest()


@transaction.atomic
def join_family(request):
    """"""
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    print(request.POST["token"])
    family: Family = FamilyInvite.objects.get(token=request.POST["token"]).family_id

    FamilyUser.objects.create(
        family_id=family,
        custom_user_id=request.user,
        is_manager=False
    )
    return JsonResponse(data={
        'alert-message': get_locale_text(
            request=request, ID="family-create-success",
            default_text="Welcome to FamilyThings, %PLACEHOLDER%!",
            insert=request.user.full_name()),
        'alert-type': 'success'
        })


@transaction.atomic
def create_invite(request):
    family: Family = FamilyUser.objects.filter(
            custom_user_id=request.user)[request.session["current_family"]].family_id

    old_invite: FamilyInvite = FamilyInvite.objects.get(family_id=family)
    old_invite.delete()

    new_invite: FamilyInvite = FamilyInvite.objects.create(
        family_id=family,
        generated_by=request.user,
        token=get_random_string(length=40)
    )

    return JsonResponse(data={
        'alert-message': get_locale_text(
            request=request, ID="new-invite-created",
            default_text="New invite has been created."),
        'alert-type': 'warning',
        'new-token': new_invite.token
        })


@transaction.atomic
def remove_from_family(request):
    print(request.POST)
    target: FamilyUser = FamilyUser.objects.get(family_id=request.POST["family_id"], custom_user_id=request.POST["user_id"])
    target.delete()

    return JsonResponse(data={
        'alert-message': 'User has been removed from family.',
        'alert-type': 'warning'
        })
