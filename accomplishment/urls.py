from django.urls import path, re_path
from . import views
from . import requests

# Ideally, its name is identical with the folder's
app_name = "accomplishment"

urlpatterns = [
     # path(<URL>, <view>, <name>)
     re_path(r"^(?:show=(?P<popup>[a-zA-Z_]+)/)?$", views.page_overview, name="overview"),

     # AJAX Urls
     re_path(r"^get/(?:amount=(?P<amount>[0-9]+)/)?(?:start=(?P<start>[0-9]+)/)?(?:selector='(?P<selector>[a-zA-Z]+)'/)?(?:key='(?P<key>[0-9a-zA-Z ]+)')?$",
          requests.get_entries, name="get"),
     path("get/recent/amount=<int:amount>",
          requests.get_recent, name="get_recent"),
     path("get/today/amount=<int:amount>",
          requests.get_obtained_today, name="obtained_today"),
     path("get/name=<str:name>",
          requests.get_by_name, name="get_by_name"),
     path("get/names",
          requests.get_names, name="get_names"),

     path("entry/get/id=<uuid:ID>",
          requests.get_accomp_by_id, name="get_by_id"),
     path("entry/edit/id=<uuid:ID>",
          requests.edit_accomp, name="edit_accomp"),
     path("entry/repeat",
          requests.repeat_accomplishment, name="repeat_accomp"),
     path("template/get", requests.get_template, name="get_template"),
     path("template/save", requests.save_template, name="save_template"),

     # Operations (Creating/Deleting)
     path("submit",
          requests.submit_accomplishment, name="submit_new"),
     path("delete/id=<uuid:ID>",
          requests.delete_accomplishment, name="delete"),
]
