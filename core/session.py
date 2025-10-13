from functools import wraps
import json
from django.contrib.messages import add_message
from django.http import JsonResponse
from django.shortcuts import redirect

from .models import FamilyUser


def list_get(source_list: list, index: int, default):
    try:
        return source_list[index]
    except IndexError:
        return default


def update_user_session(require_login: bool = True, *args, **kwargs):

    def decorator(func, *args, **kwargs):
        @wraps(func)
        def inner(*args, **kwargs):
            request = args[0]
            lang_code: str = kwargs.get("lang_code", "")
            cache_last_visited_page: bool = kwargs.get("cache_last_visited_page", True)
            print(require_login)

            if require_login:
                if not request.user.is_authenticated:
                    create_alert(request=request, ID="login-required", type="warning",
                                text="For this action, you need to login first.")
                    return redirect("core:user_login")

                try:
                    FamilyUser.objects.filter(
                        custom_user_id=request.user)[request.session["current_family"]]
                except (FamilyUser.DoesNotExist, IndexError):
                    return redirect("core:user_final_step")

            if cache_last_visited_page:
                request.session["last_visited_page"] = request.get_full_path()

            #  Handling being in multiple Families at once
            #  This is fallback to prevent an IndexError
            if (request.session.get("current_family", -1) == -1):
                request.session["current_family"] = 0

            if request.user.is_authenticated:
                # First, get all Families tied to the user
                family_queue = FamilyUser.objects.filter(
                    custom_user_id=request.user).order_by('join_date')

                if len(family_queue) > 0:
                    # Then, create a list with all the family names
                    request.session["families"] = list(family_queue.values_list("family_id__name"))
                    # Also grab a dict with all the relevant info about the family you're
                    # currently switched to
                    request.session["family_info"] = family_queue[request.session["current_family"]].serialized()

            #  Apply a language code based on either the existing value,
            #  an User's own setting, or lastly, the browser's.
            if lang_code == "":
                request.session['lang_code'] = request.session.get(
                    'lang_code', request.LANGUAGE_CODE)
            else:
                request.session['lang_code'] = lang_code

            # Fallback if there is no language_code
            if request.session['lang_code'] == "":
                request.session['lang_code'] = "en"

            #  If a User disables the custom cursor, it needs to be
            #  passed onto the session.
            if (request.user.is_authenticated):
                request.session['use_custom_cursor'] = request.user.cursor
            else:
                request.session['use_custom_cursor'] = True

            return func(*args)

        return inner

    return decorator


# TODO: Switch to the new 'update_user_session' everywhere, then remove this.
def update_session(request, lang_code: str = "", custom_cursor: bool = True,
                   cache_last_visited_page: bool = True):
    """Updates the User's session as needed"""

    if cache_last_visited_page:
        request.session["last_visited_page"] = request.get_full_path()

    #  Handling being in multiple Families at once
    #  This is fallback to prevent an IndexError
    if (request.session.get("current_family", -1) == -1):
        request.session["current_family"] = 0

    if request.user.is_authenticated:
        # First, get all Families tied to the user
        family_queue = FamilyUser.objects.filter(
            custom_user_id=request.user).order_by('join_date')

        if len(family_queue) > 0:
            # Then, create a list with all the family names
            request.session["families"] = list(family_queue.values_list("family_id__name"))
            # Also grab a dict with all the relevant info about the family you're
            # currently switched to
            request.session["family_info"] = family_queue[request.session["current_family"]].serialized()

    #  Apply a language code based on either the existing value,
    #  an User's own setting, or lastly, the browser's.
    if lang_code == "":
        request.session['lang_code'] = request.session.get(
            'lang_code', request.LANGUAGE_CODE)
    else:
        request.session['lang_code'] = lang_code

    # Fallback if there is no language_code
    if request.session['lang_code'] == "":
        request.session['lang_code'] = "en"

    #  If a User disables the custom cursor, it needs to be
    #  passed onto the session.
    if (request.user.is_authenticated):
        request.session['use_custom_cursor'] = request.user.cursor
    else:
        request.session['use_custom_cursor'] = custom_cursor


def switch_language(request):
    """Changes the display language in the User's session"""
    request.session['lang_code'] = request.POST.get(
        "lang_code", request.LANGUAGE_CODE)

    create_alert(request=request, ID="language-changed",
                 type="warning", text="Language changed into English.")

    return JsonResponse(
        data={
            'result': 'success',
            'lang_code': 'lang_code'
            }
        )


def switch_family(request, id: 0):
    """Changes the display language in the User's session"""
    request.session['current_family'] = id

    # create_alert(request=request, ID="language-changed",
    #              type="warning", text="Language changed into English.")

    return redirect("core:user_profile")


def create_alert(request: dict, type: str = "", ID: str = "",
                 text: str = "", insert: str = " "):
    """Create a message to pass onto the User's session"""
    message: str = text

    # Try to load one of localization files.
    try:
        file: str = f"./static/localization/{request.session['lang_code']}/alerts.json"
        raw_json: str = open(file, encoding='utf-8').read()
        parsed_json = json.loads(raw_json)
        message = parsed_json[ID]
    # Otherwise, proceed with the default text.
    except (Exception):
        pass

    add_message(
        request=request,
        level=20,
        message=message.replace("%PLACEHOLDER%", insert),
        extra_tags=type.replace("error", "danger")
    )


def get_locale_text(request: dict, ID: str = "",
                    default_text: str = " ", insert: str = " ") -> str:
    # Try to load one of localization files.
    try:
        file: str = f"./static/localization/{request.session['lang_code']}/alerts.json"
        raw_json: str = open(file, encoding='utf-8').read()
        parsed_json = json.loads(raw_json)
        return parsed_json[ID].replace("%PLACEHOLDER%", insert)
    # Otherwise, proceed with the default text.
    except (Exception):
        return default_text.replace("%PLACEHOLDER%", insert)


class JsonResponseAlert(JsonResponse):
    def __init__(self, request, message: str, ID: str = "",
                 type: str = 'danger', insert: str = ""):
        super().__init__(
            data={
                'alert-message': get_locale_text(
                    request=request, ID=ID,
                    default_text=message, insert=insert),
                'alert-type': 'success'
            }
        )
