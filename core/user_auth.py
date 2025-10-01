from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from core.models.custom_user import CustomUser
from core.session import create_alert, get_locale_text, JsonResponseAlert


def process_login(request, lang_code: str = ""):
    """Create the Login view and/or attempt to authenticate the User."""
    if request.POST:
        username = request.POST["username"]
        password = request.POST["password"]
        auth_user = authenticate(request, username=username, password=password)

        if auth_user is not None:
            auth_user: CustomUser

            login(request, auth_user)
            auth_user.last_login = timezone.now()

            # Overwrite the session to include the user's language setting
            request.session["lang_code"] = auth_user.lang_code

            # Create this JSONResponce so that the JavaScript part of the Log In page proceeds
            return JsonResponse(
                data={
                    'alert-message': get_locale_text(
                        request=request, ID="login-success",
                        default_text="Welcome back, %PLACEHOLDER%!", insert=auth_user.full_name()),
                    'alert-type': 'success'
                    })
        else:
            return HttpResponseBadRequest(
                get_locale_text(
                        request=request, ID="login-failed",
                        default_text="Username and password don't match up with an existing account."))
    else:
        return HttpResponseBadRequest()

def process_logout(request):
    create_alert(request=request, ID="logout-success", type="warning",
                    text="You were successfully logged out.")
    logout(request)
    return redirect("core:user_login")
