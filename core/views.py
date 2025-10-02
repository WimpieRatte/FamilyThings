import re
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import EmailMessage
from django.contrib import messages
from django.conf import settings
from django.urls import reverse

from core.models.custom_user import CustomUser
from core.forms.user_settings import UserSettingsForm
from django.contrib import messages
from core.session import update_session
from core.models.password_reset import PasswordReset
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

			return redirect('core:user_login')
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

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        
        try:
            user = CustomUser.objects.get(email=email)
            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()
            password_reset_url = reverse('core:reset_password', kwargs={'reset_id': new_password_reset.reset_id})
            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'
            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
            
            email_message = EmailMessage(
				'Reset your password', # email subject
				email_body,
				settings.EMAIL_HOST_USER, # email sender
				[email] # email receiver
			)
            email_message.fail_silently = True
            email_message.send()
            return redirect('core:password_reset_sent', reset_id=new_password_reset.reset_id)
        except CustomUser.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('core:forgot_password')
    return render(request, 'core/forgot_password.html')

def password_reset_sent(request, reset_id):
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'core/password_reset_sent.html')
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('core:forgot_password')

def reset_password(request, reset_id):
    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            # Get values from POST data
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            # Verify that both passwords match
            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            # Verify password strength
            if len(password) < 8:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 8 characters long')

            # Verify that the reset link hasn't expired
            expiration_time = password_reset_id.created_at + timezone.timedelta(minutes=10)
            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')
                password_reset_id.delete()

            if not passwords_have_error:
                # Set password for user and delete password reset object
                user = password_reset_id.user
                user.set_password(password)
                user.save()
                password_reset_id.delete()
                messages.success(request, 'Password reset successful. Please login.')
                return redirect('core:user_login')
            else:
                # Stay on reset page with errors
                return redirect('core:reset_password', reset_id=reset_id)

        # If GET request, show reset form
        return render(request, "core/reset_password.html", {"reset_id": reset_id})

    except PasswordReset.DoesNotExist:
        messages.error(request, "Invalid or expired reset link.")
        return redirect("core:forgot_password")
