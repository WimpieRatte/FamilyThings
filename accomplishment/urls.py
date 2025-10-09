from django.urls import path, re_path
from . import views
from . import requests

# Ideally, its name is identical with the folder's
app_name = "accomplishment"

urlpatterns = [
     # path(<URL>, <view>, <name>)
     path("", views.page_overview, name="overview"),
     path("add", views.page_new_accomplishment, name="add_new"),
     path("add?repeat=<int:ID>", views.page_new_accomplishment, name="add_new"),
     path("edit/<uuid:ID>", views.page_edit_user_accomplishment, name="edit"),
     path("edit/<uuid:ID>/details", views.page_edit_accomplishment_details, name="edit_details"),

     # AJAX Urls
     re_path(r"^get/(?:amount=(?P<amount>[0-9]+)/)?(?:start=(?P<start>[0-9]+)/)?(?:selector='(?P<selector>[a-zA-Z]+)'/)?(?:key='(?P<key>[0-9a-zA-Z ]+)')?$",
          requests.get_entries, name="get"),
     path("get/recent?amount=<int:amount>",
          requests.get_recent, name="get_recent"),
     path("get/today/amount=<int:amount>",
          requests.get_obtained_today, name="obtained_today"),
     path("get/name=<str:name>",
          requests.get_by_name, name="get_by_name"),

     path("milestone/get/id=<uuid:ID>",
          requests.get_accomp_by_id, name="get_milestone_by_id"),
     path("milestone/edit/id=<uuid:ID>",
          requests.edit_accomp, name="edit_milestone"),

     # Operations (Creating/Deleting)
     path("submit",
          requests.submit_accomplishment, name="submit_new"),
     path("delete/id=<uuid:ID>",
          requests.delete_accomplishment, name="delete"),
]
