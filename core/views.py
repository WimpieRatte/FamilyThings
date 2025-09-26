from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from core.models.custom_user import CustomUser
from core.forms.user_settings import UserSettingsForm
from core.session import update_session
from accomplishment.models.accomplishment import Accomplishment


def render_if_logged_in(request, target: HttpResponse, lang_code: str = "en"):
    """Check if the User is logged in. Then, either proceed to the target page,
    or redirect them to the Login page."""
    if not request.user.is_authenticated:
        return redirect('core:user_login')
    return target


def home(request, lang_code: str = ""):
    """The landing page."""
    update_session(request=request, lang_code=lang_code)

    target: HttpResponse = render(
        request, "home/home.html",
        {})

    return target


def user_profile(request, lang_code: str = ""):
    """The User's overview section."""
    update_session(request=request, lang_code=lang_code)

    target: HttpResponse = render(
        request, "core/user_profile.html",
        {})

    return render_if_logged_in(request, target, lang_code)


def user_settings(request, lang_code: str = ""):
    """The User's settings page."""
    update_session(request=request, lang_code=lang_code)

    if (request.POST and isinstance(request.user, CustomUser)):
        print(request.POST)
        user: CustomUser = request.user
        user.first_name = request.POST['name']
        user.lang_code = request.POST['language']
        user.color = request.POST['color']
        user.cursor = True if request.POST['cursor'] == "on" else False
        user.save()

        return redirect('core:user_profile')

    user: CustomUser = request.user
    target: HttpResponse = render(
        request, "core/user_settings.html",
        {
            'colors': CustomUser.COLOR_CHOICES,
            'form': UserSettingsForm(
                data={
                    'name': user.first_name,
                    'language': user.lang_code,
                    'color': user.color,
                    'cursor': user.cursor
                })
        })

    return render_if_logged_in(request, target)


def update_user_settings(request):
    """Apply the user settings."""
    user = CustomUser.objects.get(username=request.user.username)
    user.color = request.POST.get("color", user.color)
    user.icon = request.POST.get("icon", user.icon)
    user.background_image = request.POST.get("background_image", user.background_image)
    user.updated = timezone.now()
    user.save()
    return JsonResponse(data={})


def user_login(request, lang_code: str = ""):
    """Create the Login view and/or attempt to authenticate the User."""
    update_session(request=request, lang_code=lang_code)

    # Redirect the user to the Overview if they're already logged in
    if request.user.is_authenticated:
        return redirect('core:user_profile')

    if (request.POST):
        username = request.POST["username"]
        password = request.POST["password"]
        auth_user = authenticate(request, username=username, password=password)

        if auth_user is not None:
            login(request, auth_user)
            auth_user.last_login = timezone.now()
            return redirect('core:user_profile')
    else:
        return render(request, "core/user_login.html", {
            'form': AuthenticationForm(data=request.POST)
        })


def user_logout(request):
    logout(request)
    return redirect('core:user_login')
