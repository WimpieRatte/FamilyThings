from django import forms
from ..constants import COLORS, LANGUAGES, TIMEZONES, YEARS


class UserSettingsForm(forms.Form):
    first_name = forms.CharField(
        label="First Name", max_length=20, required=False)
    last_name = forms.CharField(
        label="Last Name", max_length=20, required=False)
    birthday = forms.DateField(
        required=False,
        widget=forms.SelectDateWidget(years=YEARS),
    )
    language = forms.ChoiceField(
        label="Language", choices=LANGUAGES, required=True)
    cursor = forms.BooleanField(
        label="Use Custom Cursor", required=False)
    color = forms.ChoiceField(
        label="Color", required=True, choices=COLORS)
    user_icon = forms.FileField(required=False)
    background_image = forms.FileField(required=False)
    remove_icon = forms.BooleanField(
        label="Remove Icon", required=False)
    remove_background = forms.BooleanField(
        label="Remove Background", required=False)

    #  Add Bootstrap classes to the fields
    cursor.widget.attrs.update({"class": "form-check-input"})
    language.widget.attrs.update({"class": "form-select"})
