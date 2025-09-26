from django.http import JsonResponse


def update_session(request, lang_code: str = ""):
    """Updates the User's session as needed"""
    if lang_code == "":
        request.session['lang_code'] = request.session.get(
            'lang_code', request.LANGUAGE_CODE)
    else:
        request.session['lang_code'] = lang_code

    print(request.session['lang_code'])


def change_language(request):
    """Changes the display language in the User's session"""
    request.session['lang_code'] = request.POST.get(
        "lang_code", request.LANGUAGE_CODE)
    return JsonResponse(
        data={
            'result': 'success',
            'lang_code': 'lang_code'
            }
        )
