from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from accomplishment.models.accomplishment import Accomplishment


def get_obtained_today(request, amount: int = 4):
    """Obtain a JSON with a user's Accomplishments they obtained today"""
    if not request.user.is_authenticated:
        return HttpResponseBadRequest()
    else:
        today: timezone.datetime = timezone.now()
        return JsonResponse(data={
            'result': list(reversed(Accomplishment.objects.filter(
                created_by_id=request.user,
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
