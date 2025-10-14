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
]