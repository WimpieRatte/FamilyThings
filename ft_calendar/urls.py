from django.urls import path, re_path
from . import views

# Ideally, its name is identical with the folder's
app_name = "calendar"

urlpatterns = [
     # path(<URL>, <view>, <name>)
     re_path(r"^(?:start=(?P<start>[0-9]+)/)?$", views.page_calendar, name="calendar"),
     path("get", views.get, name="get"),
     path("create/", views.create_or_edit_calendar_entry, name="create_event"),
     path("edit/<int:event_id>/", views.create_or_edit_calendar_entry, name="calendar_edit"),
     path("delete/<int:event_id>/", views.delete_calendar_entry, name="calendar_delete"),
]