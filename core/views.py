import re
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from core.models.custom_user import CustomUser
from core.forms.user_settings import UserSettingsForm
from django.contrib import messages
from accomplishment.models.accomplishment import Accomplishment


def render_if_logged_in(request, target: HttpResponse, lang_code: str = "en"):
    """Check if the User is logged in. Then, either proceed to the target page,
    or redirect them to the Login page."""
    if not request.user.is_authenticated:
        # return user_login(request=request, lang_code=lang_code)
        return redirect('core:login')
    return target


def update_session(request, lang_code: str = ""):
    if lang_code == "":
        request.session['lang_code'] = request.session.get('lang_code', "en")
    else:
        request.session['lang_code'] = lang_code

    print(request.session['lang_code'])


def home(request, lang_code: str = ""):
    """The landing page."""
    update_session(request=request, lang_code=lang_code)
    list(messages.get_messages(request))
    target: HttpResponse = render(
        request, "home/home.html",
        {})

    return target
    
def register(request):
	if request.method == "POST":
	# get posted fields:
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		username = request.POST.get('username')
		email = request.POST.get('email')
		password = request.POST.get('password')
		# field validation:
		user_data_has_error = False
		if CustomUser.objects.filter(username=username).exists():
			user_data_has_error = True
			messages.error(request, "Username already exists")
		if CustomUser.objects.filter(email=email).exists():
			user_data_has_error = True
			messages.error(request, "Email already exists")
   
		password_pattern = r'^(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,}$'
		if not re.match(password_pattern, password):
			user_data_has_error = True
			messages.error(
                request,
                "Password must be at least 8 characters long, include one uppercase letter, and one special character"
            )
		if user_data_has_error:
			return redirect('core:registration')
		else:
			# create new user in database:
			CustomUser.objects.create_user(
			first_name=first_name,
			last_name=last_name,
			email=email,
			username=username,
			password=password
			)
			messages.success(request, "Account created. Login now")
	
			return redirect('core:login')
	else:
		return render(request,'registration/registration.html')


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

    target: HttpResponse = render(
        request, "core/user_settings.html",
        {
            'colors': CustomUser.COLOR_CHOICES,
            'form': UserSettingsForm(data=request.POST)
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
            return redirect('core:home')
    else:
        return render(request, "registration/login.html", {
            'form': AuthenticationForm(data=request.POST)
        })


def user_logout(request):
    logout(request)
    return redirect('core:login')
