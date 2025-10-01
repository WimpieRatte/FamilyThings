from django import forms
from django.utils import timezone
from ..models.custom_user import CustomUser


class UserSettingsForm(forms.Form):
    YEAR_CHOICES = list(reversed(range(1960, timezone.now().year-13)))

    first_name = forms.CharField(
        label="First Name", max_length=20, required=False)
    last_name = forms.CharField(
        label="Last Name", max_length=20, required=False)
    birthday = forms.DateField(
        required=False,
        widget=forms.SelectDateWidget(years=YEAR_CHOICES),
    )
    language = forms.ChoiceField(
        label="Language", choices=CustomUser.LANG_CHOICES, required=True)
    cursor = forms.BooleanField(
        label="Use Custom Cursor", required=False)
    color = forms.ChoiceField(
        label="Color", required=True, choices=CustomUser.COLOR_CHOICES)
    user_icon = forms.FileField(required=False)
    background_image = forms.FileField(required=False)
    remove_icon = forms.BooleanField(
        label="Remove Icon", required=False)
    remove_background = forms.BooleanField(
        label="Remove Background", required=False)

    #  Add Bootstrap classes to the fields
    cursor.widget.attrs.update({"class": "form-check-input"})
    language.widget.attrs.update({"class": ".form-select"})
