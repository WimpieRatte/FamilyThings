import django_tables2 as tables
from django.utils.html import format_html
from django.urls import reverse
from .models import TransactionPattern, TransactionCategory

class TransactionPatternTable(tables.Table):
    actions = tables.Column(empty_values=(), orderable=False, verbose_name='Actions')
    transaction_category_id = tables.Column(linkify=True)  # Makes category name clickable

    class Meta:
        model = TransactionPattern
        template_name = "django_tables2/bootstrap5.html"
        fields = ("business_entity_name", "transaction_category_id")
        per_page = 30
        attrs = {
            'class': 'table table-striped bg-opacity-50',
            'thead': {'class': 'fs-sm'}
        }

    def render_actions(self, record):
        return format_html(
            '<button class="btn btn-sm btn-outline-primary me-1" '
            'hx-get="{}" '
            'hx-target="closest tr" '
            'hx-swap="outerHTML">Edit</button>'
            '<button class="btn btn-sm btn-outline-danger" '
            'hx-delete="{}" '
            'hx-target="closest tr" '
            'hx-confirm="Are you sure?">Delete</button>',
            record.get_edit_url(), record.get_delete_url()
        )

    # This ensures category links work after editing as well
    def render_transaction_category_id(self, value, record):
        # This creates a link to the category edit page
        return format_html(
            '<a href="{}" class="text-decoration-none">{}</a>',
            reverse('finance:transaction_category_edit', args=[record.transaction_category_id.pk]),
            value
        )

class TransactionCategoryTable(tables.Table):
    transaction_pattern_count = tables.Column(verbose_name='Transaction Pattern Count', orderable=True)
    actions = tables.Column(empty_values=(), orderable=False, verbose_name='Actions')

    class Meta:
        model = TransactionCategory
        template_name = "django_tables2/bootstrap5.html"
        fields = ("name", "description", "family_id")
        per_page = 30

    def render_actions(self, record):
        return format_html(
            '<button class="btn btn-sm btn-outline-primary me-1" '
            'hx-get="{}" '
            'hx-target="closest tr" '
            'hx-swap="outerHTML">Edit</button>'
            '<button class="btn btn-sm btn-outline-danger" '
            'hx-delete="{}" '
            'hx-target="closest tr" '
            'hx-confirm="Are you sure you want to delete {}?">Delete</button>',
            record.get_edit_url(), record.get_delete_url(), record.name
        )

    def render_transaction_pattern_count(self, value, record):
        # Use the annotated transaction_pattern_count if available, otherwise count
        return value if hasattr(record, 'transaction_patterns_of_category') else record.transaction_patterns_of_category.count()