from django.urls import path
from . import views

# Ideally, its name is identical with the folder's
app_name = "finance"

urlpatterns = [
	path('importtransactions', views.import_transactions, name="import_transactions"),
 	path('importprofiles', views.load_import_profiles, name="import_profiles"),
	path('import_profile_controls', views.import_profile_controls, name='import_profile_controls'),
	path('save_import_profile', views.save_import_profile, name='save_import_profile'),
	path('delete_import_profile', views.delete_import_profile, name='delete_import_profile'),
 	path('save_import_profile_mapping', views.save_import_profile_mapping, name='save_import_profile_mapping'),
  	path('delete_import_profile_mapping/<int:pk>', views.delete_import_profile_mapping, name='delete_import_profile_mapping'),
	path('create_category', views.create_category, name='create_category'),
 	path('create_category_and_update_selects', views.create_category_and_update_selects, name='create_category_and_update_selects'),
 	path('category_controls', views.category_controls, name='category_controls'),
	path('edit_categories', views.edit_categories, name='edit_categories'),
 	path('save_transaction_category', views.save_transaction_category, name='save_transaction_category'),
	path('delete_transaction_category', views.delete_transaction_category, name='delete_transaction_category'),
	path('load_headers', views.load_headers, name='load_headers'),

	# Transaction Pattern URLs
	# TODO: Phase out these old transaction pattern URLs in favor of DataTable 2 design.
    path('transaction-patterns/', views.transaction_patterns, name='transaction_patterns'),
    path('transaction-patterns/create/', views.create_transaction_pattern, name='create_transaction_pattern'),
    path('transaction-patterns/update/<int:pattern_id>/', views.update_transaction_pattern, name='update_transaction_pattern'),
    path('transaction-patterns/delete/<int:pattern_id>/', views.delete_transaction_pattern, name='delete_transaction_pattern'),
    # Transaction Pattern URLs for Data Table 2 designs
    path('transaction-patterns-list/', views.TransactionPatternListView.as_view(), name='transaction_pattern_list'),
    path('transaction-patterns-list/new/', views.TransactionPatternCreateView.as_view(), name='transaction_pattern_create'),
    path('transaction-patterns-list/<int:pk>/edit/', views.edit_transaction_pattern_row, name='transaction_pattern_edit'),
    path('transaction-patterns-list/<int:pk>/delete/', views.delete_transaction_pattern_row, name='transaction_pattern_delete'),

    # Transaction Category URLs
    path('transaction_categories/', views.TransactionCategoryListView.as_view(), name='transaction_category_list'),
    path('transaction_categories/new/', views.TransactionCategoryCreateView.as_view(), name='transaction_category_create'),
    path('transaction_categories/<int:pk>/edit/', views.edit_transaction_category_row, name='transaction_category_edit'),
    path('transaction_categories/<int:pk>/delete/', views.delete_transaction_category_row, name='transaction_category_delete'),
]