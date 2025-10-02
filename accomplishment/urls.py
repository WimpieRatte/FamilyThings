from django.urls import path
from . import views
from . import requests

# Ideally, its name is identical with the folder's
app_name = "accomplishment"

urlpatterns = [
    # path(<URL>, <view>, <name>)
    path("", views.overview_page, name="overview"),
    path("add", views.add_new_page, name="add_new"),
    path("add?repeat=<int:ID>", views.add_new_page, name="add_new"),

    # AJAX Urls
    path("get/recent?amount=<int:amount>",
         requests.get_recent, name="get_recent"),
    path("get/today/amount=<int:amount>",
         requests.get_obtained_today, name="obtained_today"),
    path("get/name=<str:name>",
         requests.get_by_name, name="get_by_name"),

    path("?submit",
         requests.submit_accomplishment, name="submit_new"),
]
