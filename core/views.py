import re
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import AnonymousUser
from core.models.custom_user import CustomUser
from core.models.family_user import FamilyUser
from core.forms import UserSettingsForm, UserRegisterForm

from core.session import update_session, create_alert, get_locale_text
from accomplishment.models.accomplishment import Accomplishment


def render_if_logged_in(request, target: HttpResponse):
    """Check if the User is logged in. Then, either proceed to the target page,
    or redirect them to the Login page."""
    if not request.user.is_authenticated:
        create_alert(request=request, ID="login-required", type="warning",
            text="For this action, you need to login first.")
        return redirect("core:user_login")
    return target


def home(request, lang_code: str = ""):
    """The landing page."""
    update_session(request=request, lang_code=lang_code)
    target: HttpResponse = render(request, "home/home.html", {})

    return target


PASSWORD_PATTERN = r"^(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,}$"
def user_register(request):
    form: UserRegisterForm = UserRegisterForm()

    if request.method == "POST":
        form = UserRegisterForm(data=request.POST)

        # get posted fields:
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            first_name = form.cleaned_data.get("first_name", "")
            last_name = form.cleaned_data.get("last_name", "")

            # field validation:
            user_data_has_error = False
            if CustomUser.objects.filter(username=username).exists():
                user_data_has_error = True
                create_alert(request=request, ID="user-exists", type="error",
                    text="This Username is already taken.")
            if CustomUser.objects.filter(email=email).exists():
                user_data_has_error = True
                create_alert(request=request, ID="email-used", type="error",
                    text="There is already an account tied to this email.")

            if not re.match(PASSWORD_PATTERN, password):
                user_data_has_error = True
                create_alert(request=request, ID="password-invalid", type="error",
                    text="Password must be at least 8 characters long, include one uppercase letter, and one special character.")

        if user_data_has_error:
            return redirect("core:user_register")
        else:
            # create new user in database:
            new_user: CustomUser = CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            create_alert(request=request, ID="account-created", type="success",
                    text="Account has been successfully created. You may login now.")

            Accomplishment.objects.create(
                created_by=new_user,
                name="First Step",
                description="Create an Account",
                icon="person-arms-up",
                type=None,
                measurement=None
            )
            return redirect("core:user_login")
    else:
        return render(
            request, "core/user_register.html",
            {'form': form})


def user_profile(request, lang_code: str = ""):
    """The User's overview section."""
    update_session(request=request, lang_code=lang_code)
    today: timezone.datetime = timezone.now()

    target: HttpResponse = render(request, "core/user_profile.html", {
        'is_family_member': FamilyUser.objects.filter(
            custom_user_id=request.user)
    })

    return render_if_logged_in(request, target)


def user_settings(request, lang_code: str = ""):
    """The User's settings page."""
    update_session(request=request, lang_code=lang_code)

    if isinstance(request.user, AnonymousUser):
        create_alert(request=request, ID="login-required", type="warning",
            text="For this action, you need to login first.")
        return redirect("core:user_login")

    user: CustomUser = request.user

    #  We need to check for the birthday to prevent an AttributeError
    birthday = ""
    if user.birthday is not None:
        birthday = f"{user.birthday.year}-{user.birthday.day}-{user.birthday.month}"

    form: UserSettingsForm = UserSettingsForm(
        #  Autofill form based on existing user settings
        data={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "language": user.lang_code,
            "color": user.color,
            "cursor": user.cursor,
            "birthday": birthday
        }
    )

    if request.POST:
        form = UserSettingsForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            user.first_name = form.cleaned_data.get("first_name")
            user.last_name = form.cleaned_data.get("last_name")
            user.birthday = form.cleaned_data.get("birthday")
            user.lang_code = form.cleaned_data.get("language")
            user.color = form.cleaned_data.get("color")
            user.cursor = form.cleaned_data.get("cursor", False)

            #  Upload and update the icon and background, if required
            if form.cleaned_data.get("user_icon") is not None:
                user.icon = form.cleaned_data.get("user_icon")

            if form.cleaned_data.get("background_image") is not None:
                user.background_image = form.cleaned_data.get(
                    "background_image")

            # Remove icon and background
            if form.cleaned_data.get("remove_icon"):
                user.icon = None

            if form.cleaned_data.get("remove_background"):
                user.background_image = None

            user.updated = timezone.now()
            update_session(
                request=request,
                lang_code=request.POST["language"],
                custom_cursor=user.cursor,
            )
            user.save()
            create_alert(request=request, ID="settings-updated", type="success",
                text="Your settings have been saved.")

        return redirect("core:user_profile")

    target: HttpResponse = render(
        request,
        "core/user_settings.html",
        {
            "colors": CustomUser.COLOR_CHOICES,
            "form": UserSettingsForm(
                #  Autofill form based on existing user settings
                data={
                    "name": user.first_name,
                    "language": user.lang_code,
                    "color": user.color,
                    "cursor": user.cursor,
                    "user_icon": user.icon,
                    "background_image": user.background_image,
                }
            ),
        },
    )
    return render_if_logged_in(request=request, target=target)


def user_login(request, lang_code: str = ""):
    """Create the Login view and/or attempt to authenticate the User."""
    update_session(request=request, lang_code=lang_code)

    # Redirect the user to the Overview if they're already logged in
    if request.user.is_authenticated:
        return redirect("core:user_profile")

    return render(
        request, "core/user_login.html", {
            "form": AuthenticationForm(data=request.POST)})


def user_logout(request):
    create_alert(request=request, ID="logout-success", type="warning",
                    text="You were successfully logged out.")
    logout(request)
    return redirect("core:user_login")
