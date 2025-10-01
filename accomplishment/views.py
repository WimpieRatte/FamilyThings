from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from core.views import render_if_logged_in
from core.session import update_session, create_alert, get_locale_text
from core.models.custom_user import CustomUser
from .models.accomplishment import Accomplishment



def overview(request, lang_code: str = ""):
    """An overview of an User's Accomplishments."""
    update_session(request=request, lang_code=lang_code)

    if not request.user.is_authenticated:
        create_alert(request=request, ID="login-required", type="warning",
            text="For this action, you need to login first.")
        return redirect("core:user_login")

    target: HttpResponse = render(
        request, "accomplishment/overview.html",
        {
            'recent_accomplishments': Accomplishment.objects.filter(
                created_by=request.user)
        })

    return render_if_logged_in(request, target)
