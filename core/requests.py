from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from core.models import Family, FamilyUser
from core.forms import UserFinalizeForm
from core.session import get_locale_text

from accomplishment.models import Accomplishment
from messenger.models import Message, FamilyChat


def create_family(request):
    """Obtain a JSON with a user's recent Accomplishments"""
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
