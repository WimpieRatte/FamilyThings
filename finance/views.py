from .forms import TransactionCategoryForm, TransactionPatternForm
from .models import ImportProfile, ImportProfileMapping, TransactionCategory, TransactionPattern
from .tables import TransactionCategoryTable, TransactionPatternTable
from core.session import update_session, create_alert
from core.views import render_if_logged_in
from core.models import FamilyUser
from core.utils import ImportProfileMappingDestinationColumns, text_to_enum_destination_column
from decimal import Decimal, InvalidOperation
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView
from django_tables2 import SingleTableView, RequestConfig
import plotly.graph_objects as go
import plotly.express as px
import json  # add this line near the top with the other imports
import pandas as pd
import html
import io


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
        pass
    else:
        pass
    return HttpResponse("")

def create_category_and_update_selects(request):
    """Create Category via fetch API"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    # get current family from session
    fam_user = FamilyUser.objects.filter(
        custom_user_id=request.user)[request.session["current_family"]]
    family = fam_user.family_id

    # Get category name from POST data
    category_name = request.POST.get('category_name', '').strip()
    if not category_name:
        return JsonResponse({'success': False, 'error': 'Category name cannot be empty'})

    print(f"Creating category: {category_name}")

    try:
        category, created = TransactionCategory.objects.get_or_create(
            name=category_name,
            family_id=family
        )

        if not created:
            return JsonResponse({'success': False, 'error': 'Category already exists'})

        # Return the new category data as JSON
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name
            }
        })

    except Exception as e:
        print(f"Error creating category: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

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
        columns_to_extract = set()  # using a set prevents duplicates added.
        column_names_lookup = {}
        for mapping in import_profile_mappings:
            columns_to_extract.add(mapping.from_file_header)
            column_names_lookup[mapping.to_transaction_header] = mapping.from_file_header

        try:
            # Read file
            if uploaded_file.name.lower().endswith('.csv'):
                uploaded_file.seek(0)  # rewind just in case
                # TextIOWrapper decodes the binary stream into text for pandas.
                with io.TextIOWrapper(uploaded_file.file, encoding="utf-8", errors="ignore") as text_stream:
                    df = pd.read_csv(text_stream, sep=None, engine="python")  # This should auto-detect the separator
            else:
                uploaded_file.seek(0)  # rewind just in case
                df = pd.read_excel(uploaded_file)

            # Extract only the columns specified in the Import Profile:
            df_reordered = extract_specific_columns(df, columns_to_extract)

            # Rename the column headers to the ones specified in the Import Profile:
            inverted_dict = {v: k for k, v in column_names_lookup.items()}
            df_reordered.rename(columns=inverted_dict, inplace=True)

            # region Transaction Pattern matching

            # Get all Transaction Patters for all Transaction Categories this family has:
            transaction_patterns = TransactionPattern.objects.filter(transaction_category_id__family_id=family_id)
            if len(transaction_patterns) > 0 and "Business Entity Name" in df_reordered.columns:
                # Convert it to a dictionary for easy usage with dataframe
                transaction_patterns_as_dict = {pattern.business_entity_name: pattern.transaction_category_id.id for pattern in transaction_patterns}

                # Mapping for category based on TransactionPattern matching
                try:
                    # Explicitly convert to Series and then map
                    business_names_series = df_reordered["Business Entity Name"].squeeze()  # Convert single-column DataFrame to Series
                    mapped_categories = business_names_series.map(transaction_patterns_as_dict)
                    df_reordered['suggested_category'] = mapped_categories.fillna(-1)
                except Exception as e:
                    print(f"Error in mapping: {e}")
                    df_reordered['suggested_category'] = categories[0].id
            else:
                # No Transaction Patterns defined yet, so default to the first category
                df_reordered['suggested_category'] = categories[0].id

            # Convert DataFrame to HTML with dropdowns
            results = generate_html_with_dropdowns(df_reordered, categories)
            html_output = results['html_output']
            row_categories = results['row_categories']

            # endregion

            context.update({
                'success': True,
                'result': df_reordered.to_dict("records"),
                'row_count': len(df_reordered),
                "html_output": html_output,
                "row_categories": row_categories,
                "detected_categories": sum(1 for value in row_categories.values() if value != -1)
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
    """Generate HTML table with category dropdowns. Returns a dictionary containing the generated HTML output and a mapping of row indexes to their corresponding categories."""
    html_output = '<table id="transactions-table" class="table table-striped table-bordered">\n'

    # Header row
    html_output += '<thead><tr>'
    header_counter = 0
    for column in df.columns:
        if column != 'suggested_category':  # Don't show suggested category column
            html_output += f'<th>{html.escape(str(column))}</th>'
            header_counter += 1
    html_output += f'<th>Category</th>'
    html_output += '</tr></thead>\n'

    # Data rows
    html_output += '<tbody>'
    row_categories = {}  # will store the indexes of each row and their corresponding categories
    for index, row in df.iterrows():
        html_output += '<tr>'

        # Data columns
        for column in df.columns:
            if column != 'suggested_category':
                value = str(row[column]) if pd.notna(row[column]) else ''
                # If Amount column, give it a specific class name
                if column == 'Amount':
                    html_output += f'<td class="amount-column">{value}</td>'
                else:
                    html_output += f'<td>{html.escape(value)}</td>'

        # Category dropdown
        suggested_category = row['suggested_category']
        html_output += f'<td>'
        html_output += f'<select name="category_{index}" class="form-select category-select">'
        # First add select prompt
        if suggested_category == -1:
            selected = 'selected'
            row_categories[index] = -1
        else:
            selected = ''
        html_output += f'<option value="-1" {selected} disabled>Select...</option>'
        # Then add the other options
        for category in categories:
            if category.id == suggested_category:
                selected = 'selected'
                row_categories[index] = category.id
            else:
                selected = ''
            html_output += f'<option value="{category.id}" {selected}>{html.escape(category.name)}</option>'

        html_output += '</select>'
        # html_output += f'<input type="hidden" name="suggested_category_{index}" value="{html.escape(suggested_category)}">'
        html_output += '</td>'

        html_output += '</tr>\n'
    html_output += '</tbody></table>'

    return {"html_output": html_output, "row_categories": row_categories}

@require_http_methods(["POST"])
def save_imported_transactions(request):
    try:
        data = json.loads(request.body)
        table_structure = data.get('table_structure', [])
        table_data = data.get('table_data', [])

        results = []

        for row_data in table_data:
            try:
                # Determine model based on your logic
                # This could be passed from frontend or determined by context
                model_name = "Transaction"  # or get from request/session
                model = apps.get_model('finance', model_name)

                # Handle lookups and foreign keys
                processed_data = {}
                for header in table_structure:
                    field_name = header['field']
                    value = row_data.get(field_name)

                    if header.get('lookup') and value:
                        # Handle foreign key lookups
                        lookup_model = apps.get_model('finance', header['lookup'])
                        if value.isdigit():
                            # Value is ID
                            processed_data[field_name + '_id'] = value
                        else:
                            # Value is display name - need to find or create
                            lookup_obj, created = lookup_model.objects.get_or_create(
                                name=value
                            )
                            processed_data[field_name + '_id'] = lookup_obj.id
                    else:
                        processed_data[field_name] = value

                # Save or update record
                if row_data.get('id'):
                    # Update existing
                    obj = model.objects.get(id=row_data['id'])
                    for key, value in processed_data.items():
                        setattr(obj, key, value)
                    obj.save()
                else:
                    # Create new
                    obj = model.objects.create(**processed_data)

                results.append({'success': True, 'id': obj.id})

            except Exception as e:
                results.append({'success': False, 'error': str(e)})

        return JsonResponse({'success': True, 'results': results})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def transaction_patterns(request, lang_code: str = ""):
    """Transaction Patterns management view"""
    update_session(request=request, lang_code=lang_code)

    # Get current family
    fam_user = FamilyUser.objects.filter(
        custom_user_id=request.user)[request.session["current_family"]]
    family_id = fam_user.family_id

    # Get all categories and patterns for current family
    categories = TransactionCategory.objects.filter(family_id=family_id).all()
    patterns = TransactionPattern.objects.filter(transaction_category_id__family_id=family_id).all()

    context = {
        'categories': categories,
        'patterns': patterns,
    }

    return render(request, 'finance/transaction_patterns.html', context)

def create_transaction_pattern(request):
    """Create Transaction Pattern via fetch API"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    # Get current family
    fam_user = FamilyUser.objects.filter(
        custom_user_id=request.user)[request.session["current_family"]]
    family_id = fam_user.family_id

    try:
        business_entity_name = request.POST.get('business_entity_name', '').strip()
        category_id = request.POST.get('category_id', '').strip()
        transaction_pattern_id = request.POST.get('transaction_pattern_id')

        # Validate required fields
        if not business_entity_name:
            return JsonResponse({'success': False, 'error': 'Name is required'})

        if not category_id:
            return JsonResponse({'success': False, 'error': 'Category is required'})

        # Get category and verify it belongs to current family
        category = get_object_or_404(TransactionCategory, id=category_id, family_id=family_id)

        # Check if pattern id already exists:
        if transaction_pattern_id == "-1":
            # Create new pattern
            transaction_pattern = TransactionPattern.objects.create(
                business_entity_name=business_entity_name,
                transaction_category_id=category
            )
        else:
            transaction_pattern = get_object_or_404(TransactionPattern, id=transaction_pattern_id)
            transaction_pattern.business_entity_name = business_entity_name
            transaction_pattern.transaction_category_id = category
            transaction_pattern.save()

        return JsonResponse({
            'success': True,
            'pattern': {
                'id': transaction_pattern.id,
                'business_entity_name': transaction_pattern.business_entity_name,
                'category_id': transaction_pattern.transaction_category_id.id,
                'category_name': transaction_pattern.transaction_category_id.name
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def update_transaction_pattern(request, pattern_id):
    """Update Transaction Pattern via fetch API"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    # Get current family
    fam_user = FamilyUser.objects.filter(
        custom_user_id=request.user)[request.session["current_family"]]
    family_id = fam_user.family_id

    try:
        pattern = get_object_or_404(TransactionPattern, id=pattern_id, transaction_category_id__family_id=family_id)

        business_entity_name = request.POST.get('business_entity_name', '').strip()
        category_id = request.POST.get('category_id', '').strip()

        # Validate required fields
        if not business_entity_name:
            return JsonResponse({'success': False, 'error': 'Name is required'})

        if not category_id:
            return JsonResponse({'success': False, 'error': 'Category is required'})

        # Get category and verify it belongs to current family
        category = get_object_or_404(TransactionCategory, id=category_id, family_id=family_id)

        # Update the pattern
        pattern.business_entity_name = business_entity_name
        pattern.transaction_category_id = category
        pattern.save()

        return JsonResponse({
            'success': True,
            'pattern': {
                'id': pattern.id,
                'business_entity_name': pattern.business_entity_name,
                'category_id': pattern.transaction_category_id.id,
                'category_name': pattern.transaction_category_id.name
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def delete_transaction_pattern(request, pattern_id):
    """Delete Transaction Pattern"""

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    try:
        pattern = get_object_or_404(TransactionPattern, id=pattern_id)
        pattern_name = pattern.business_entity_name
        pattern.delete()

        return JsonResponse({
            'success': True,
            'message': f'Pattern "{pattern_name}" deleted successfully'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# region Datatable 2 views

class TransactionPatternListView(SingleTableView):
    model = TransactionPattern
    table_class = TransactionPatternTable
    template_name = 'finance/transaction_pattern_list.html'
    paginate_by = 30

    def get_template_names(self):
        if self.request.htmx and not self.request.htmx.boosted:
            return ['finance/partials/transaction_pattern_list_partial.html']
        return [self.template_name]

    def get_queryset(self):
        queryset = super().get_queryset().select_related('transaction_category_id')

        # Filter by transaction category if provided
        transaction_category_id = self.request.GET.get('transaction_category_id')
        if transaction_category_id:
            queryset = queryset.filter(transaction_category_id=transaction_category_id)

        return queryset.order_by('business_entity_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # First get family_id
        fam_user = FamilyUser.objects.filter(custom_user_id=self.request.user)[self.request.session["current_family"]]
        family_id = fam_user.family_id

        # Then get all categories for current family
        context['transaction_categories'] = TransactionCategory.objects.filter(family_id=family_id).order_by('name').all()
        return context

def create_transaction_pattern_row(request):
    """Handle inline transaction pattern creation"""

    # Get family_id:
    fam_user = FamilyUser.objects.filter(custom_user_id=request.user)[request.session["current_family"]]
    family_id = fam_user.family_id

    if request.method == "POST":

        form = TransactionPatternForm(request.POST)
        if form.is_valid():
	        # Cater for possible hidden/session dependant values:
            if not form.instance.pk:
                form.instance.family_id = family_id
            transaction_pattern = form.save()
            # Return the new row
            table = TransactionPatternTable(TransactionPattern.objects.filter(transaction_category_id__family_id=family_id))
            for row in table.rows:
                if row.record.pk == transaction_pattern.pk:
                    return HttpResponse(row)
    else:
        # Return form with errors
        return render(request, 'finance/partials/transaction_pattern_create_row.html', {'form': form})

    # GET request - show creation form
    form = TransactionPatternForm()
    return render(request, 'finance/partials/transaction_pattern_create_row.html', {
        'form': form
    })

def edit_transaction_pattern_row(request, pk):
    transaction_pattern = get_object_or_404(TransactionPattern, pk=pk)

    # Get family_id:
    fam_user = FamilyUser.objects.filter(custom_user_id=request.user)[request.session["current_family"]]
    family_id = fam_user.family_id

    if request.method == "POST":
        form = TransactionPatternForm(request.POST, instance=transaction_pattern)
        if form.is_valid():
	        # Cater for possible hidden/session dependant values:
            if not form.instance.pk:
                form.instance.family_id = family_id
            form.save()
            # Return the updated row
            return render(request, 'finance/partials/transaction_pattern_table_row.html', {
                'record': transaction_pattern,
                'table': TransactionPatternTable(TransactionPattern.objects.filter(transaction_category_id__family_id=family_id))
            })
        else:
            # Return form with errors
            return render(request, 'finance/partials/transaction_pattern_edit_row.html', {
                'form': form,
                'transaction_pattern': transaction_pattern
            })

    # GET request - show edit form
    form = TransactionPatternForm(instance=transaction_pattern)
    return render(request, 'finance/partials/transaction_pattern_edit_row.html', {
        'form': form,
        'transaction_pattern': transaction_pattern
    })

def delete_transaction_pattern_row(request, pk):
    transaction_pattern = get_object_or_404(TransactionPattern, pk=pk)
    if request.method == "DELETE":
        transaction_pattern.delete()
        return HttpResponse('')  # Empty response removes the row

    return HttpResponse(status=405)  # Method not allowed

class TransactionPatternCreateView(CreateView):
    model = TransactionPattern
    form_class = TransactionPatternForm
    template_name = 'finance/transaction_pattern_form.html'
    success_url = reverse_lazy('transaction_pattern_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Get current family_id:
        fam_user = FamilyUser.objects.filter(custom_user_id=self.request.user)[self.request.session["current_family"]]
        family_id = fam_user.family_id

        # Pass hidden/session values from session to the form
        kwargs['family_id'] = family_id
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.htmx:
            # Return a redirect that HTMX will follow
            return HttpResponse(
                f'<div hx-get="{self.success_url}" hx-trigger="load" hx-target="body"></div>'
            )
        return response

class TransactionCategoryListView(SingleTableView):
    model = TransactionCategory
    table_class = TransactionCategoryTable
    template_name = 'finance/transaction_category_list.html'
    paginate_by = 30

    def get_template_names(self):
        if self.request.htmx and not self.request.htmx.boosted:
            return ['finance/transaction_category_list_partial.html']
        return [self.template_name]

    def get_queryset(self):
        return TransactionCategory.objects.annotate(
            transaction_pattern_count=Count('transaction_patterns_of_category')
        ).order_by('name')

def create_transaction_category_row(request):
    """Handle inline transaction category creation"""

    # Get family_id:
    fam_user = FamilyUser.objects.filter(custom_user_id=request.user)[request.session["current_family"]]
    family_id = fam_user.family_id

    if request.method == "POST":
        form = TransactionCategoryForm(request.POST)
        if form.is_valid():
	        # Cater for possible hidden/session dependant values:
            if not form.instance.pk:
                form.instance.family_id = family_id
            transaction_category = form.save()
            # Return the new row
            table = TransactionCategoryTable(TransactionCategory.objects.filter(family_id=family_id))
            for row in table.rows:
                if row.record.pk == transaction_category.pk:
                    return HttpResponse(row)
    else:
        # Return form with errors
        return render(request, 'finance/partials/transaction_category_create_row.html', {'form': form})

    # GET request - show creation form
    form = TransactionCategoryForm()
    return render(request, 'finance/partials/transaction_category_create_row.html', {
        'form': form
    })


def edit_transaction_category_row(request, pk):
    transaction_category = get_object_or_404(TransactionCategory, pk=pk)

    # Get family id:
    fam_user = FamilyUser.objects.filter(custom_user_id=request.user)[request.session["current_family"]]
    family_id = fam_user.family_id

    if request.method == "POST":
        form = TransactionCategoryForm(request.POST, instance=transaction_category)
        if form.is_valid():
	        # Cater for possible hidden/session dependant values:
            if not form.instance.pk:
                form.instance.family_id = family_id
            form.save()
            # Return the updated row
            return render(request, 'finance/partials/transaction_category_table_row.html', {
                'record': transaction_category,
                'table': TransactionCategoryTable(TransactionCategory.objects.filter(family_id=family_id)),
            })
        else:
            return render(request, 'finance/partials/transaction_category_edit_row.html', {
                'form': form,
                'transaction_category': transaction_category
            })

    form = TransactionCategoryForm(instance=transaction_category)
    return render(request, 'finance/partials/transaction_category_edit_row.html', {
        'form': form,
        'transaction_category': transaction_category
    })

def delete_transaction_category_row(request, pk):
    transaction_category = get_object_or_404(TransactionCategory, pk=pk)
    if request.method == "DELETE":
        # Check if category has products
        if transaction_category.transaction_patterns_of_category.exists():
            return HttpResponse(
                '<div class="alert alert-danger">Cannot delete transaction category with associated transaction patterns.</div>',
                status=400
            )
        transaction_category.delete()
        return HttpResponse('')
    return HttpResponse(status=405)

class TransactionCategoryCreateView(CreateView):
    model = TransactionCategory
    form_class = TransactionCategoryForm
    template_name = 'finance/transaction_category_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Get current family_id:
        fam_user = FamilyUser.objects.filter(custom_user_id=self.request.user)[self.request.session["current_family"]]
        family_id = fam_user.family_id

        # Pass hidden/session values from session to the form
        kwargs['family_id'] = family_id
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.htmx:
            return HttpResponse(
                f'<div hx-get="{reverse("finance:transaction_category_list")}" hx-trigger="load" hx-target="body"></div>'
            )
        return response

    def get_success_url(self):
        return reverse('finance:transaction_category_list')
# endregion