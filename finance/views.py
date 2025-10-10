from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from core.session import update_session, create_alert
from core.views import render_if_logged_in
from .models import ImportProfile, ImportProfileMapping
from core.models import FamilyUser
from django.http import JsonResponse

# Create your views here.
def import_transactions(request, lang_code: str = ""):
    """An overview of an User's Accomplishments."""
    update_session(request=request, lang_code=lang_code)

    if not request.user.is_authenticated:
        create_alert(request=request, ID="login-required", type="warning",
            text="For this action, you need to login first.")
        return redirect("core:user_login")

    profiles_list = ImportProfile.objects.prefetch_related().all()
    context = {
        "profiles": profiles_list
    }

    target: HttpResponse = render(request, "finance/import_transactions.html", context=context)
    return render_if_logged_in(request, target)

def import_profiles(request, lang_code: str = ""):
    """An screen showing the import profiles and allowing the user to edit its column mapping."""
    update_session(request=request, lang_code=lang_code)

    if not request.user.is_authenticated:
        create_alert(request=request, ID="login-required", type="warning",
            text="For this action, you need to login first.")
        return redirect("core:user_login")

    selected_profile_id = request.GET.get('import_profile_selector')

    profiles_list = ImportProfile.objects.prefetch_related().all()
    context = {
        "profiles": profiles_list,
        "selected_profile_id": selected_profile_id
    }

    target: HttpResponse = render(request, "finance/import_profiles.html", context=context)
    return render_if_logged_in(request, target)

def import_profile_controls(request, lang_code: str = ""):
    """Partial screen that shows the controls to edit the import profile."""
    update_session(request=request, lang_code=lang_code)

    import_profile_id = request.GET.get('import_profile_selector')
    if import_profile_id is None or len(import_profile_id) == 0:
        return redirect("finance:import_profiles")

    import_profile = ImportProfile.objects.get(id=import_profile_id)
    context = {
        "profile": import_profile,
    }
    return render(request, "finance/partials/import_profile_controls.html", context=context)

def save_import_profile(request):
    """Save a new or edited Import Profile."""

    # test for POST
    if request.POST.get('action') == 'post':
        # get existing ImportProfile, if id is found:
        profile_id = request.POST.get('profile_id')
        if profile_id != "":
            import_profile = ImportProfile.objects.get(pk=profile_id)
        else:
            import_profile = ImportProfile()

        # update with new values
        import_profile.name = request.POST.get('profile_name')
        import_profile.description = request.POST.get('profile_description')
        fam_user = FamilyUser.objects.filter(
            custom_user_id=request.user)[request.session["current_family"]]
        import_profile.family_id = fam_user.family_id

        # save changes
        import_profile.save()

        # Return response
        return JsonResponse({'profile_id': import_profile.id})
    else:
        return JsonResponse({'status': False})

def delete_import_profile(request):
    pass