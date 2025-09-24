from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
# from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from core.models.custom_user import CustomUser
from accomplishment.models.accomplishment import Accomplishment


def target_if_logged_in(request, target: HttpResponse, lang_code: str = "en"):
    if not request.user.is_authenticated:
        return user_login(request=request, lang_code=lang_code)
    return target


# Create your views here.
def home(request, lang_code: str = "en"):
    """The landing page."""

    target: HttpResponse = render(
        request, "home/home.html",
        {
            # TODO: Modify to display real accomplishments
            'lang_code': lang_code,
            'recent_accomplishments': Accomplishment.objects.filter()
        })

    return target_if_logged_in(request, target, lang_code)


def user_settings(request):
    """The settings page."""

    target: HttpResponse = render(
        request, "core/user_settings.html",
        {
            'colors': CustomUser.COLOR_CHOICES
        })

    return target_if_logged_in(request, target)


def update_user_settings(request):
    """Apply the user settings."""
    user = CustomUser.objects.get(username=request.user.username)
    user.color = request.POST.get("color", user.color)
    user.icon = request.POST.get("icon", user.icon)
    user.background_image = request.POST.get("background_image", user.background_image)
    user.save()
    return JsonResponse(data={})


def user_login(request, lang_code: str = "en"):
    if (request.POST):
        username = request.POST["username"]
        password = request.POST["password"]
        auth_user = authenticate(request, username=username, password=password)

        if auth_user is not None:
            login(request, auth_user)
            return redirect('core:home')
    else:
        return render(request, "registration/login.html", {
            # TODO: Modify to display real accomplishments
            'lang_code': lang_code,
            'form': AuthenticationForm(data=request.POST)
        })


def user_logout(request, lang_code: str = "en"):
    logout(request)
    return redirect('core:login')
