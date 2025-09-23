from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "core"  # ideally, name it the same as the foldername of your app

urlpatterns = [
    # path(<URL>, <view>, <name>)
    path("", include("django.contrib.auth.urls")),
    path("", views.home, name="home"),
    path("accounts/profile/", views.home, name="home"),  # default landing page
    path("log_out", views.log_out),
    path("settings", views.user_settings, name="user_settings"),

    # Unused
    path("settings/update", views.update_user_settings,
         name="user_settings_update"),
    path("test", views.update_user_settings, name="update_user_settings"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
