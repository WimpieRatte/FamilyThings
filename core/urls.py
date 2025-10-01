from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from core.session import change_language
from . import views
from . import user_auth

# Ideally, its name is identical with the folder's
app_name = "core"

core_urls = [
    # path(<URL>, <view>, <name>)
    path("", views.home, name="home"),
    path("login/", views.user_login_page, name="user_login"),
    path("register/", views.user_register, name="user_register"),
    path("profile/", views.user_profile_page, name="user_profile"),
    path("settings/", views.user_settings_page, name="user_settings"),

    # Authentication and session (AJAX)
    path("auth?log_in", user_auth.process_login, name="request_login"),
    path("auth?log_out", user_auth.process_logout, name="request_logout"),
    path("session?switch_language", change_language,
         name="session_change_language"),
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
