from django import forms
from ..models.custom_user import CustomUser


class UserSettingsForm(forms.Form):
    name = forms.CharField(label="Name",
                           max_length=20, required=False)
    language = forms.ChoiceField(label="Language",
                                 choices=CustomUser.LANG_CHOICES,
                                 required=True)
    cursor = forms.BooleanField(label="Use Custom Cursor", required=True)
    color = forms.ChoiceField(label="Color", required=True,
                              choices=CustomUser.COLOR_CHOICES)
    user_icon = forms.FileField(required=False)
    background_image = forms.FileField(required=False)
