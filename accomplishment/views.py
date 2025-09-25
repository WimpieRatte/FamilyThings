from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from core.views import render_if_logged_in
from core.models.custom_user import CustomUser
from .models.accomplishment import Accomplishment


def overview(request, lang_code: str = "en"):
    """An overview of an User's Accomplishments."""

    target: HttpResponse = render(
        request, "accomplishment/overview.html",
        {
            'recent_accomplishments': Accomplishment.objects.filter(
                created_by=request.user)
        })

    return render_if_logged_in(request, target, lang_code)
