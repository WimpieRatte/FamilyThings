from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from core.session import update_session, create_alert
from core.views import render_if_logged_in
from .models import ImportProfile, ImportProfileMapping, TransactionCategory, TransactionPattern
from core.models import FamilyUser
from django.http import JsonResponse
from core.utils import ImportProfileMappingDestinationColumns, text_to_enum_destination_column
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import plotly.graph_objects as go
import plotly.express as px
from django.template.loader import render_to_string
import json  # add this line near the top with the other imports
import pandas as pd
import html

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

    # Get all categories for the current family:
    categories = TransactionCategory.objects.filter(family_id=family_id).all()

    # Build context
    context = {
        "profiles": profiles_list,
        "chart_html": chart_html,
        "categories": categories
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

def create_category(request):
    """Create Category via HTMX postback"""
    # get current family from session
    fam_user = FamilyUser.objects.filter(
        custom_user_id=request.user)[request.session["current_family"]]
    family = fam_user.family_id

    category_name = request.headers.get('txtCategoryNameValue')
    if category_name.strip() == "":
        print(f"Empty category name!")
        return HttpResponse("")
    print(f"category_name={category_name}")
    category, created = TransactionCategory.objects.get_or_create(
                            name=category_name,
                            family_id=family
                        )

    if not created:
        print("Category already exists!")
        return HttpResponse("")

    # Check if we're on the "import_transactions" screen:
    requested_from = request.headers.get('X-Current-Path', 'Unknown')
    if requested_from == "import_transactions":
        # we're targeting the .category_select_boxes class divs, which need new select boxes:
        categories = TransactionCategory.objects.all()
        context = {"categories": categories}
        return render(request, "finance/partials/category_select_box.html", context=context)
    elif requested_from == "edit_categories":
        # TODO:
        pass
    else:
        # TODO:
        pass
    return HttpResponse("")

def edit_categories(request, lang_code: str = ""):
    """Edit Categories"""
    update_session(request=request, lang_code=lang_code)

    # Get current family
    fam_user = FamilyUser.objects.filter(
        custom_user_id=request.user)[request.session["current_family"]]
    family_id = fam_user.family_id

    # Get the selected Transaction Category, or select the first one available:
    transaction_category_id = request.GET.get('selected_transaction_category')
    # print(f"transaction_category_id={transaction_category_id}")
    if transaction_category_id is None or transaction_category_id in ("-1", ""):
        first_transaction_category = TransactionCategory.objects.filter(family_id=family_id).first()
        if first_transaction_category is None:
            transaction_category_id = -1
        else:
            transaction_category_id = first_transaction_category.id

    # Get all categories for current family
    categories = TransactionCategory.objects.filter(family_id=family_id).all()
    context = {
        "categories": categories,
        "selected_transaction_category": int(transaction_category_id)
    }
    return render(request, "finance/edit_categories.html", context=context)

@login_required(login_url='user_login')
def save_transaction_category(request):
    """Save a new or edited Transaction Category."""
    # test for POST
    if request.POST.get('action') == 'post':
        # get existing TransactionCategory, if id is found:
        transaction_category_id = request.POST.get('transaction_category_id')
        # print(f"transaction_category_id: {transaction_category_id}")
        if transaction_category_id is None or transaction_category_id in ("None", "", "-1"):  # Since its received as a post get, it's been converted to "None" as an str.
            transaction_category = TransactionCategory()
        else:
            transaction_category = TransactionCategory.objects.get(pk=transaction_category_id)

        # update with new values
        transaction_category.name = request.POST.get('transaction_category_name')
        transaction_category.description = request.POST.get('transaction_category_description')
        # get current family from session
        fam_user = FamilyUser.objects.filter(
            custom_user_id=request.user)[request.session["current_family"]]
        transaction_category.family_id = fam_user.family_id

        # save changes
        transaction_category.save()

        # Return response
        return JsonResponse({'transaction_category_id': transaction_category.id})
    else:
        return JsonResponse({'status': False})

@login_required(login_url='user_login')
def delete_transaction_category(request):
    """Delete a specific Transaction Category."""

    # test for POST
    if request.POST.get('action') == 'post':
        # get existing TransactionCategory, if id is found:
        transaction_category_id = request.POST.get('transaction_category_id')
        if transaction_category_id != "":
            transaction_category = TransactionCategory.objects.get(pk=transaction_category_id)
        else:
            return JsonResponse({'status': False})

        # delete record from database
        transaction_category.delete()

        # Return response
        return JsonResponse({'transaction_category_id': transaction_category.id})
    else:
        return JsonResponse({'status': False})

@login_required(login_url='user_login')
def category_controls(request, lang_code: str = ""):
    """Partial screen that shows the controls to edit the transaction category."""
    update_session(request=request, lang_code=lang_code)

    # Get the selected Import Profile from the combobox:
    transaction_category_id = request.GET.get('transaction_category_selector')

    # If no import profile was selected, select the first one available:
    if transaction_category_id is None:
        transaction_category_id = TransactionCategory.objects.first().id

    # If nothing exists, just use an empty Import Profile instance:
    if transaction_category_id is None or transaction_category_id in ("-1", ""):
        transaction_category = TransactionCategory()
    else:
        transaction_category = TransactionCategory.objects.get(id=int(transaction_category_id))

    context = {
        "transaction_category": transaction_category,
        "selected_transaction_category": int(transaction_category_id)
    }
    return render(request, "finance/partials/transaction_category_controls.html", context=context)

def load_headers(request, lang_code: str = ""):
    """Load Headers"""
    update_session(request=request, lang_code=lang_code)
    context = {}

    # Get current family
    fam_user = FamilyUser.objects.filter(
        custom_user_id=request.user)[request.session["current_family"]]
    family_id = fam_user.family_id

    # Get all categories for current family
    categories = TransactionCategory.objects.filter(family_id=family_id).all()
    context["categories"] = categories


    # Load all headers from file:
    if request.method == 'POST' and request.FILES.get('formFile'):
        uploaded_file = request.FILES['formFile']

        # Get selected Import Profile's Custom Mapping:
        import_profile = ImportProfile.objects.get(pk=request.POST.get('import_profile_selector'))
        import_profile_mappings = ImportProfileMapping.objects.filter(import_profile_id=import_profile.id).all()
        columns_to_extract = []
        column_names_lookup = {}
        for mapping in import_profile_mappings:
            columns_to_extract.append(mapping.from_file_header)
            column_names_lookup[mapping.to_transaction_header] = mapping.from_file_header

        try:
            # Read file
            if uploaded_file.name.lower().endswith('.csv'):
                df = pd.read_csv(uploaded_file, sep=None, engine='python')  # This should auto-detect the separator
            else:
                df = pd.read_excel(uploaded_file)

            # Extract only the columns specified in the Import Profile:
            df_reordered = extract_specific_columns(df, columns_to_extract)

            # Rename the column headers to the ones specified in the Import Profile:
            df_reordered.rename(columns=column_names_lookup, inplace=True)

            # print the new headers:
            print("Updated headers:")
            print(df_reordered.columns.tolist())

            # region Transaction Pattern matching

            # # Get all Transaction Patters for all Transaction Categories this family has:
            # transaction_patterns = TransactionPattern.objects.filter(category_id__family_id=family_id).all()

            # # Mapping for category based on TransactionPattern matching
            # def get_suggested_category(row):
            #     """Determine suggested category based on historical TransactionPattern"""

            #     # If there are no Transaction Patterns defined, don't bother trying to match them:
            #     if len(transaction_patterns) == 0:
            #         return None
            #     # If there are no Transaction Patterns mapped to name, don't bother trying to match them:
            #     if column_names_lookup.get(ImportProfileMappingDestinationColumns.NAME.value) is None:
            #         return None

            #     # Get column that has the recipient name:
            #     recipient = str(row.get(column_names_lookup[ImportProfileMappingDestinationColumns.NAME.value], ''))
            #     return transaction_patterns.filter(name_regex=recipient).first().transaction_category_id

            # # Add suggested category column for each row
            # df['suggested_category'] = df_reordered.apply(get_suggested_category, axis=1)

            # # Convert DataFrame to HTML with dropdowns
            # html_output = generate_html_with_dropdowns(df_reordered, categories)
            # *** then continue here ***

            # endregion

            context.update({
                'success': True,
                'column_names': columns_to_extract,
                'result': df_reordered.to_dict("records"),
                'row_count': len(df_reordered)
            })

            return render(request, 'finance/partials/imported_transactions.html', context)

        except Exception as e:
            context['error'] = f'Unexpected error: {str(e)}'
            return render(request, 'finance/partials/imported_transactions.html', context)


    return render(request, "finance/partials/imported_transactions.html", context=context)

def extract_specific_columns(df, desired_order):
    """Extract DataFrame columns based on a list of column names"""
    # Get columns that exist in both DataFrame and desired order
    common_columns = [col for col in desired_order if col in df.columns]

    return df[common_columns]

def generate_html_with_dropdowns(df, categories):
    # TODO: *** first continue here ***
    """Generate HTML table with category dropdowns"""
    html_output = '<table class="table table-striped table-bordered">\n'

    # Header row
    html_output += '<thead><tr>'
    for column in df.columns:
        if column != 'suggested_category':  # Don't show suggested category column
            html_output += f'<th>{html.escape(str(column))}</th>'
    html_output += '<th>Category</th>'
    html_output += '</tr></thead>\n'

    # Data rows
    html_output += '<tbody>'
    for index, row in df.iterrows():
        html_output += '<tr>'

        # Data columns
        for column in df.columns:
            if column != 'suggested_category':
                value = str(row[column]) if pd.notna(row[column]) else ''
                html_output += f'<td>{html.escape(value)}</td>'

        # Category dropdown
        suggested_category = row['suggested_category']
        html_output += f'<td>'
        html_output += f'<select name="category_{index}" class="form-select category-select">'

        for category in categories:
            selected = 'selected' if category == suggested_category else ''
            html_output += f'<option value="{html.escape(category)}" {selected}>{html.escape(category)}</option>'

        html_output += '</select>'
        html_output += f'<input type="hidden" name="suggested_category_{index}" value="{html.escape(suggested_category)}">'
        html_output += '</td>'

        html_output += '</tr>\n'
    html_output += '</tbody></table>'

    # Add submit button
    html_output += '''
    <div class="mt-3">
        <button type="button" class="btn btn-success" onclick="submitCategories()">
            Save Categories
        </button>
    </div>
    '''

    return html_output