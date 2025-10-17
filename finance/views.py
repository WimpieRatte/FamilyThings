from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from core.session import update_session, create_alert
from core.views import render_if_logged_in
from .models import ImportProfile, ImportProfileMapping
from core.models import FamilyUser
from django.http import JsonResponse
from core.utils import ImportProfileMappingDestinationColumns, text_to_enum_destination_column
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import plotly.graph_objects as go
import plotly.express as px
from django.template.loader import render_to_string
import json  # add this line near the top with the other imports

# Create your views here.
@login_required(login_url='user_login')
def import_transactions(request, lang_code: str = ""):
    """An overview of an User's Accomplishments."""
    update_session(request=request, lang_code=lang_code)

    if not request.user.is_authenticated:
        create_alert(request=request, ID="login-required", type="warning",
            text="For this action, you need to login first.")
        return redirect("core:user_login")

    # Get current family from session, to filter by:
    fam_user = FamilyUser.objects.filter(
	    custom_user_id=request.user)[request.session["current_family"]]
    family_id = fam_user.family_id

    # Get all profiles for the current family:
    profiles_list = ImportProfile.objects.filter(family_id=family_id).all().prefetch_related()

    # Load the chart
    # TODO: Replace the sample below with actual data retrieval logic
    labels = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports']
    values = [45000, 35000, 28000, 42000, 19000]
    fig = go.Figure(
        data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker_colors=px.colors.qualitative.Set3
        )]
    )
    fig.update_layout(title='Distribution by Category', height=500)

    chart_json = json.loads(fig.to_json())  # convert JSON string to dict

    chart_html = render_to_string(
        'reports/finance/plotly_pie_chart.html',
        {
            'chart_title': 'Category Distribution',
            'chart_description': 'This chart shows the distribution of transactions across different categories.',
            'chart_json': chart_json,
        }
    )

    # Build context
    context = {
        "profiles": profiles_list,
        "chart_html": chart_html,
    }

    target: HttpResponse = render(request, "finance/import_transactions.html", context=context)
    return render_if_logged_in(request, target)

@login_required(login_url='user_login')
def load_import_profiles(request, lang_code: str = ""):
    """An screen showing the import profiles and allowing the user to edit its column mapping."""
    update_session(request=request, lang_code=lang_code)

    if not request.user.is_authenticated:
        create_alert(request=request, ID="login-required", type="warning",
            text="For this action, you need to login first.")
        return redirect("core:user_login")

    # Get the selected Import Profile, or select the first one available:
    import_profile_id = request.GET.get('selected_import_profile')
    if import_profile_id is None:
        first_import_profile = ImportProfile.objects.first()
        if first_import_profile is None:
            import_profile_id = -1
        else:
            import_profile_id = first_import_profile.id

    # Get current family from session, to filter by:
    fam_user = FamilyUser.objects.filter(
	    custom_user_id=request.user)[request.session["current_family"]]
    family_id = fam_user.family_id
    # For the combobox, get all rows for the current family:
    profiles_list = ImportProfile.objects.prefetch_related().filter(family_id=family_id).all()

    # For the table, get all mappings for the selected Import Profile:
    mappings_list = ImportProfileMapping.objects.filter(import_profile_id=import_profile_id).all()

    # For the destination dropdowns, get all transaction headers:
    destination_columns = [(column.name, column.value) for column in ImportProfileMappingDestinationColumns]

    context = {
        "profiles": profiles_list,
        "selected_import_profile": int(import_profile_id),
        "mappings": mappings_list,
        "destination_columns": destination_columns
    }

    target: HttpResponse = render(request, "finance/import_profiles.html", context=context)
    return render_if_logged_in(request, target)

@login_required(login_url='user_login')
def import_profile_controls(request, lang_code: str = ""):
    """Partial screen that shows the controls to edit the import profile."""
    update_session(request=request, lang_code=lang_code)

    # Get the selected Import Profile from the combobox:
    import_profile_id = request.GET.get('import_profile_selector')

    # If no import profile was selected, select the first one available:
    if import_profile_id is None:
        import_profile_id = min([x.id for x in ImportProfile.objects.all()])

    # If nothing exists, just use an empty Import Profile instance:
    if import_profile_id is None or import_profile_id == "-1":
        import_profile = ImportProfile()
    else:
        import_profile = ImportProfile.objects.get(id=int(import_profile_id))

    context = {
        "profile": import_profile,
        "selected_import_profile": import_profile_id
    }
    return render(request, "finance/partials/import_profile_controls.html", context=context)

@login_required(login_url='user_login')
def save_import_profile(request):
    """Save a new or edited Import Profile."""
    # test for POST
    if request.POST.get('action') == 'post':
        # get existing ImportProfile, if id is found:
        profile_id = request.POST.get('profile_id')
        if profile_id == "None":  # Since its received as a post get, it's been converted to "None" as an str.
            import_profile = ImportProfile()
        else:
            import_profile = ImportProfile.objects.get(pk=profile_id)

        # update with new values
        import_profile.name = request.POST.get('profile_name')
        import_profile.description = request.POST.get('profile_description')
        # get current family from session
        fam_user = FamilyUser.objects.filter(
            custom_user_id=request.user)[request.session["current_family"]]
        import_profile.family_id = fam_user.family_id

        # save changes
        import_profile.save()

        # Return response
        return JsonResponse({'profile_id': import_profile.id})
    else:
        return JsonResponse({'status': False})

@login_required(login_url='user_login')
def delete_import_profile(request):
    """Delete a specific Import Profile."""

    # test for POST
    if request.POST.get('action') == 'post':
        # get existing ImportProfile, if id is found:
        profile_id = request.POST.get('profile_id')
        if profile_id != "":
            import_profile = ImportProfile.objects.get(pk=profile_id)
        else:
            return JsonResponse({'status': False})

        # delete record from database
        import_profile.delete()

        # Return response
        return JsonResponse({'profile_id': import_profile.id})
    else:
        return JsonResponse({'status': False})

@login_required(login_url='user_login')
def save_import_profile_mapping(request):
    """Save a new or edited Import Profile Mapping."""

    # get existing ImportProfileMapping, if id is found:
    mapping_id = request.POST.get('mapping_id')
    if mapping_id in ("-1", ""):  # Since its received as a post get, it's been converted to "None" as an str.
        import_profile_mapping = ImportProfileMapping()
    else:
        import_profile_mapping = ImportProfileMapping.objects.get(pk=mapping_id)

    # update with new values
    # Get the selected Import Profile, or select the first one available:
    import_profile_id = request.GET.get('selected_import_profile')
    if import_profile_id is None:
        first_import_profile = ImportProfile.objects.first()
        if first_import_profile is None:
            return HttpResponse('')
        else:
            import_profile_id = first_import_profile.id
            import_profile_mapping.import_profile_id = first_import_profile
    else:
        import_profile_mapping.import_profile_id = ImportProfile.objects.get(pk=import_profile_id)

    import_profile_mapping.from_file_header = request.POST.get('from_file_header')
    to_transaction_header = request.POST.get('to_transaction_header')
    to_transaction_header_enum = text_to_enum_destination_column(to_transaction_header)
    match to_transaction_header_enum:
        case ImportProfileMappingDestinationColumns.NAME:
            import_profile_mapping.to_transaction_header = ImportProfileMappingDestinationColumns.NAME.value
        case ImportProfileMappingDestinationColumns.DESCRIPTION:
            import_profile_mapping.to_transaction_header = ImportProfileMappingDestinationColumns.DESCRIPTION.value
        case ImportProfileMappingDestinationColumns.TRANSACTION_DATE:
            import_profile_mapping.to_transaction_header = ImportProfileMappingDestinationColumns.TRANSACTION_DATE.value
        case ImportProfileMappingDestinationColumns.REFERENCE:
            import_profile_mapping.to_transaction_header = ImportProfileMappingDestinationColumns.REFERENCE.value
        case ImportProfileMappingDestinationColumns.BUSINESS_ENTITY_NAME:
            import_profile_mapping.to_transaction_header = ImportProfileMappingDestinationColumns.BUSINESS_ENTITY_NAME.value
        case ImportProfileMappingDestinationColumns.AMOUNT:
            import_profile_mapping.to_transaction_header = ImportProfileMappingDestinationColumns.AMOUNT.value
        case ImportProfileMappingDestinationColumns.CURRENCY:
            import_profile_mapping.to_transaction_header = ImportProfileMappingDestinationColumns.CURRENCY.value
        case ImportProfileMappingDestinationColumns.CATEGORY:
            import_profile_mapping.to_transaction_header = ImportProfileMappingDestinationColumns.CATEGORY.value

    # save changes
    #print(import_profile_mapping)
    import_profile_mapping.save()

    # For the destination dropdowns, get all transaction headers:
    destination_columns = [(column.name, column.value) for column in ImportProfileMappingDestinationColumns]

    context = {
        "mapping": import_profile_mapping,
        "selected_import_profile": import_profile_id,
        "destination_columns": destination_columns
    }
    # Return response
    return render(request, "finance/partials/import_profile_mapping_table_row.html", context=context)

@login_required(login_url='user_login')
@require_http_methods(["DELETE"])
def delete_import_profile_mapping(request, pk: int):
    """Deletes the specific import profile mapping"""
    try:
        import_profile_mapping = get_object_or_404(ImportProfileMapping, pk=pk)
        import_profile_mapping.delete()
        return HttpResponse("")
    except Exception as e:
        print(e)
        return HttpResponse("")

