from django.urls import path, re_path
from . import views

# Ideally, its name is identical with the folder's
app_name = "calendar"

urlpatterns = [
     # path(<URL>, <view>, <name>)
     re_path(r"^(?:start=(?P<start>[0-9]+)/)?$", views.page_calendar, name="calendar"),
     path("get", views.get, name="get"),
]
