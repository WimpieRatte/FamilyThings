from django.urls import path
from . import views
from . import requests

# Ideally, its name is identical with the folder's
app_name = "accomplishment"

urlpatterns = [
    # path(<URL>, <view>, <name>)
    path("", views.overview_page, name="overview"),
    path("add", views.add_new_page, name="add_new"),

    # AJAX Urls
    path("?get_recent?amount=<int:amount>",
         requests.get_recent, name="get_recent"),
    path("?obtained_today?amount=<int:amount>",
         requests.get_obtained_today, name="obtained_today"),
    path("?submit",
         requests.submit_accomplishment, name="submit_new"),
]
