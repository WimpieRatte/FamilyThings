from django.shortcuts import render, redirect
from django.http import HttpResponse
from core.views import render_if_logged_in
from core.session import update_session, create_alert, get_locale_text
from core.models.custom_user import CustomUser
from .forms.accomplishment import AccomplishmentForm
from .models.accomplishment import Accomplishment
from .models.family_user_accomplishment import FamilyUserAccomplishment
from . import constants


def overview_page(request, lang_code: str = ""):
    """An overview of an User's Accomplishments."""
    update_session(request=request, lang_code=lang_code)

    if not request.user.is_authenticated:
        create_alert(request=request, ID="login-required", type="warning",
            text="For this action, you need to login first.")
        return redirect("core:user_login")

    recent_additions = Accomplishment.objects.filter(
                    created_by=request.user.id).order_by('created').values()[:10]

    target: HttpResponse = render(
        request, "accomplishment/overview.html",
        {
            'recent_additions': list(reversed(Accomplishment.objects.filter(id__in=recent_additions))),
            'colors': ['red', 'blue', 'green', 'orange', 'purple', 'cyan']
        })

    return render_if_logged_in(request, target)


def add_new_page(request, lang_code: str = "", ID: int = -1):
    """."""
    update_session(request=request, lang_code=lang_code,
                   cache_last_visited_page=False)
    form: AccomplishmentForm = AccomplishmentForm()

    if ID is not -1:
        accom: Accomplishment = Accomplishment.objects.get(id=ID)
        form = AccomplishmentForm(initial={
            'name': accom.name,
            'description': accom.description,
            'icon': accom.icon,
            'measurement_quantity': 1
        })

    return render(
        request, "accomplishment/add_new.html",
        {
            "form": form,
            "icons": constants.ICONS
        })
