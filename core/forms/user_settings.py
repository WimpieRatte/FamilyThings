from django import forms
from ..models.custom_user import CustomUser


class UserSettingsForm(forms.Form):
    name = forms.CharField(label="Name", max_length=20)
    language = forms.ChoiceField(choices=CustomUser.LANG_CHOICES)
    cursor = forms.BooleanField()
