from django.urls import path
from . import views
from . import requests

# Ideally, its name is identical with the folder's
app_name = "accomplishment"

urlpatterns = [
    # path(<URL>, <view>, <name>)
    path("", views.overview, name="overview"),

    # AJAX Urls
    path("?get_recent?amount=<int:amount>",
         requests.get_recent, name="get_recent"),
    path("?obtained_today?amount=<int:amount>",
         requests.get_obtained_today, name="obtained_today"),
]
