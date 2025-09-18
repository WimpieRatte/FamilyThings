from django.urls import path
from . import views
app_name = "core"  # ideally, name it the same as the foldername of your app

urlpatterns = [
	# path(<URL>, <view>, <name>)
	path("", views.home, name="home"),  # default landing page
]