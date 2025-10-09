from django.http import HttpResponse
from django.shortcuts import render, redirect
from core.session import update_session, create_alert
from core.views import render_if_logged_in

# Create your views here.
def import_transactions(request, lang_code: str = ""):
    """An overview of an User's Accomplishments."""
    update_session(request=request, lang_code=lang_code)

    if not request.user.is_authenticated:
        create_alert(request=request, ID="login-required", type="warning",
            text="For this action, you need to login first.")
        return redirect("core:user_login")

    target: HttpResponse = render(request, "finance/import_transactions.html")

    return render_if_logged_in(request, target)