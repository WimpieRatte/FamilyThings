from django.urls import path, re_path
from . import views

# Ideally, its name is identical with the folder's
app_name = "calendar"

urlpatterns = [
     # path(<URL>, <view>, <name>)
     path("", views.page_calendar, name="calendar"),
]
