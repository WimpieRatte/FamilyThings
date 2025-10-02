from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from core.session import update_session, change_language
from . import views

# Ideally, its name is identical with the folder's
app_name = "core"

core_urls = [
    # path(<URL>, <view>, <name>)
    path("", views.home, name="home"),
    path("login/", views.user_login, name="user_login"),  # Django's default
    path("logout/", views.user_logout, name="user_logout"),
    path("registration/", views.register, name="registration"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("password_reset_sent/<str:reset_id>/", views.password_reset_sent, name="password_reset_sent"),
    path("reset_password/<str:reset_id>/", views.reset_password, name="reset_password"),
    path("profile/", views.user_profile, name="user_profile"),
    path("settings/", views.user_settings, name="user_settings"),
    path("accounts/profile/", views.home, name="home"),  # default landing page
   

    # AJAX Urls
    path("session/switchlanguage", change_language,
         name="session_change_language"),

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
