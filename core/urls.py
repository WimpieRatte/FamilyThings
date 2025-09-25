from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from . import views

# Ideally, its name is identical with the folder's
app_name = "core"

core_urls = [
    # path(<URL>, <view>, <name>)
    path("", views.home, name="home"),
    path("login/", LoginView.as_view(), name="login"),  # Django's default
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.user_profile, name="user_profile"),
    path("settings/", views.user_settings, name="user_settings"),
    path("accounts/profile/", views.home, name="home"),  # default landing page
    path("registration/", views.register, name="registration"),

    # Unused
    path("settings/update/", views.update_user_settings,
         name="user_settings_update"),
    path("test/", views.update_user_settings, name="update_user_settings"),
]

urlpatterns = [
    # Import core_urls twice to include variants
    # with and without a provided language code
    re_path(r"^(?P<lang_code>[a-z]{2,3})/", include(core_urls)),
    path("", include(core_urls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
