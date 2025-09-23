from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import logout
from .models.accomplishment import Accomplishment
from .models.custom_user import CustomUser


# Create your views here.
def home(request):
    """The landing page."""
    if not request.user.is_authenticated:
        return redirect("core:login")

    return render(
        request, "home/home.html",
        {'todo': Accomplishment.objects.filter(),
         'colors': CustomUser.COLOR_CHOICES})


def user_settings(request):
    """The settings page."""
    # return HttpResponse("Hello World!")  # This will also work
    return render(
        request, "core/user_settings.html",
        {'colors': CustomUser.COLOR_CHOICES})


def update_user_settings(request):
    """The settings page."""
    user = CustomUser.objects.get(username=request.user.username)
    user.color = request.POST.get("color", user.color)
    user.icon = request.POST.get("icon", user.icon)
    user.background_image = request.POST.get("background_image", user.background_image)
    user.save()
    return JsonResponse(data={})


def log_out(request):
    logout(request)
    return redirect("core:login")
