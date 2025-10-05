from django.urls import path, re_path
from . import views
from . import requests

# Ideally, its name is identical with the folder's
app_name = "accomplishment"

urlpatterns = [
    # path(<URL>, <view>, <name>)
    path("", views.overview_page, name="overview"),
    path("start=<int:start>", views.overview_page, name="overview"),
    path("add", views.add_new_page, name="add_new"),
    path("add?repeat=<int:ID>", views.add_new_page, name="add_new"),

    # AJAX Urls
    re_path(r"^get/(?:amount=(?P<amount>[0-9]+)/)?(?:start=(?P<start>[0-9]+)/)?(?:key=(?P<key>[0-9a-zA-Z]+)/)?$",
         requests.get_entities, name="get"),
    path("get/recent?amount=<int:amount>",
         requests.get_recent, name="get_recent"),
    path("get/today/amount=<int:amount>",
         requests.get_obtained_today, name="obtained_today"),
    path("get/name=<str:name>",
         requests.get_by_name, name="get_by_name"),

    path("?submit",
         requests.submit_accomplishment, name="submit_new"),
]
