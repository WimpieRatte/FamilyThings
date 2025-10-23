import re
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import EmailMessage
from django.contrib import messages
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, redirect

from core.session import update_user_session
from .constants import COLORS
from .models import CustomUser, Family, FamilyUser, FamilyInvite, PasswordReset
from .forms import UserSettingsForm, UserRegisterForm, UserFinalizeForm
from .requests import join_family
from .session import update_session, create_alert

from accomplishment.models import FamilyUserAccomplishment
from messenger.models import FamilyChat, Message
from ft_calendar.models import CalendarEntry


# TODO: Switch to the new 'update_user_session' everywhere, then remove this.
def render_if_logged_in(request, target: HttpResponse):
    """Check if the User is logged in. Then, either proceed to the target page,
    or redirect them to the Login/Final Step page."""

    if not request.user.is_authenticated:
        create_alert(request=request, ID="login-required", type="warning",
                     text="For this action, you need to login first.")
        return redirect("core:user_login")

    try:
        FamilyUser.objects.filter(
            custom_user_id=request.user)[request.session["current_family"]]
        return target
    except (FamilyUser.DoesNotExist, IndexError):
        return redirect("core:user_final_step")


@update_user_session(require_login=False)
def home(request):
    """The Home page."""
    return render(request, "home/home.html", {})


PASSWORD_PATTERN = r"^(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,}$"


@transaction.atomic
@update_user_session(require_login=False)
def user_register(request):

    # Redirect the user to the Overview if they're already logged in
    if request.user.is_authenticated:
        return redirect("core:user_profile")

    form: UserRegisterForm = UserRegisterForm()

    if request.method != "POST":
        return render(
            request, "core/user_register.html",
            {'form': form})
    else:
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
                create_alert(
                    request=request, ID="email-used", type="error",
                    text="There is already an account tied to this email.")

            if not re.match(PASSWORD_PATTERN, password):
                user_data_has_error = True
                create_alert(
                    request=request, ID="password-invalid", type="error",
                    text="Password must be at least 8 characters long, include\
                         one uppercase letter, and one special character.")

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

                if form.data.get("invite_code", "") != "":
                    # It is required for the user to be logged in before
                    # attempting to use the invite
                    login(request, new_user)
                    join_family(request, token=form.data.get("invite_code"))

                    logout(request)

                CalendarEntry.objects.create(
                    title="First Step",
                    description="Created your FamilyThings account",
                    custom_user_id=new_user
                )

                create_alert(
                    request=request, ID="account-created", type="success",
                    text="Account has been successfully created. \
                        You may login now.")
                return redirect("core:user_login")


@update_user_session(require_family=False)
def user_final_step(request):
    """."""
    form: UserFinalizeForm = UserFinalizeForm(
        initial={'family_name': f"{request.user.full_name()}'s Family"})
    return render(request, "core/user_final_step.html", {'form': form})


@update_user_session()
def user_profile_page(request):
    """The User's overview section."""
    try:
        fam_user = FamilyUser.objects.get(
            custom_user_id=request.user,
            family_id=request.session["family_info"]["family_ID"])
        chat = FamilyChat.objects.filter(family_id=request.session["family_info"]["family_ID"])

        # Messenger
        # TODO: Move the Message creation to its own section
        if request.POST:
            try:
                Message.objects.create(
                    text=request.POST["text"],
                    custom_user_id=request.user,
                    family_chat_id=chat[0])
                request.POST = None
                redirect("core:user_profile")
            except (Exception):
                pass

        messages = []
        if len(chat) > 0:
            messages = Message.objects.filter(
                family_chat_id=chat[0],
                deleted=False).order_by(
                "created_on").reverse()[:10]

        #  Family Activities
        fam_users = FamilyUser.objects.filter(
            family_id=request.session["family_info"]["family_ID"]).exclude(
                custom_user_id=request.user)

        accomplishments = []
        for user in fam_users:
            try:
                user_accomp = FamilyUserAccomplishment.objects.filter(
                    family_user_id=user
                ).order_by("created").reverse()[0]

                # Get the creared/created date before proceeding with
                # the Accomplishment details.
                create_date = user_accomp.created

                user_accomp = user_accomp.accomplishment_id.serialized()
                user_accomp["cleared_by"] = user.custom_user_id.full_name()
                user_accomp["color"] = user.custom_user_id.color
                user_accomp["user_icon"] = user.custom_user_id.icon
                user_accomp["date"] = create_date
                user_accomp["fam_user_ID"] = str(user.id)
                user_accomp["email"] = user.custom_user_id.email
                accomplishments += [user_accomp]
            except (IndexError):
                pass

        return render(request, "core/user_profile.html", {
            'family': fam_user.serialized(),
            'family_activity': accomplishments,
            'chat': list(messages)
        })
    except (FamilyUser.DoesNotExist, IndexError) as e:
        print(e)
        return redirect("core:user_final_step")


@update_user_session()
def user_settings_page(request):
    """The User's settings page."""
    user: CustomUser = request.user

    #  We need to check for the birthday to prevent an AttributeError
    birthday = ""
    if user.birthday is not None:
        birthday = f"{user.birthday.year}-{user.birthday.day}-\
            {user.birthday.month}"

    form: UserSettingsForm = UserSettingsForm(
        #  Autofill form based on existing user settings
        initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "language": user.lang_code,
            "color": user.color,
            "cursor": user.cursor,
            "birthday": birthday
        }
    )

    if request.POST or request.FILES:
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
            create_alert(request=request, ID="settings-updated", 
                         type="success",
                         text="Your settings have been saved.")
        else:
            print(form.errors)

        return redirect("core:user_profile")

    return render(
        request,
        "core/user_settings.html",
        {
            "colors": COLORS,
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


@update_user_session()
def manage_family_page(request):
    """."""
    family: Family = Family.objects.get(
        id=request.session['family_info']['family_ID'])
    invite: str = "N/A"
    all_invites: list = []

    try:
        invite = FamilyInvite.objects.get(generated_by=request.user).token
    except (FamilyInvite.DoesNotExist):
        pass

    return render(request, "core/user_manage_family.html", {
        'family': family.serialized(),
        'members': list(FamilyUser.objects.filter(
            family_id=family.id, deactivated=False).order_by("join_date")),
        'invite': invite, 'all_invites': all_invites,
    })


@update_user_session(require_login=False)
def user_login_page(request):
    """Create the Login view and/or attempt to authenticate the User."""

    # Redirect the user to the Overview if they're already logged in
    if request.user.is_authenticated:
        return redirect("core:user_profile")

    return render(
        request, "core/user_login.html", {
            "form": AuthenticationForm(data=request.POST)})

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email").strip()

        try:
            # Check if user exists
            user = CustomUser.objects.get(email=email)

            # Either get existing PasswordReset for this user or create a new one
            password_reset, created = PasswordReset.objects.get_or_create(custom_user_id=user)

            # Always update timestamp (optional, to reset expiration)
            password_reset.save()

            # Build the password reset URL
            password_reset_url = reverse("core:reset_password", kwargs={"reset_id": password_reset.reset_id})
            full_password_reset_url = f"{request.scheme}://{request.get_host()}{password_reset_url}"

            # Compose email
            email_subject = "Reset your password"
            email_body = f"Reset your password using the link below:\n\n{full_password_reset_url}"
            email_message = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )

            # Send email
            email_message.fail_silently = False  # Set to False to catch errors while debugging
            email_message.send()

            # Redirect to a confirmation page
            messages.success(request, "Password reset link sent to your email.")
            return redirect("core:password_reset_sent", reset_id=password_reset.reset_id)

        except CustomUser.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found.")
            return redirect("core:forgot_password")

    # GET request: render forgot password form
    return render(request, "core/forgot_password.html")

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
            expiration_time = password_reset_id.created + timezone.timedelta(minutes=10)
            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')
                password_reset_id.delete()

            if not passwords_have_error:
                # Set password for user and delete password reset object
                user = CustomUser.objects.get(id=password_reset_id.custom_user_id.id)
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
