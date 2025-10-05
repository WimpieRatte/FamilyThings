from django import forms


class UserFinalizeForm(forms.Form):
    family_name = forms.CharField(
        label="", max_length=100, required=False)
    invite_code = forms.CharField(
        label="", max_length=50, required=False)

    family_name.widget.attrs.update({"style": "width: 20em;"})
    invite_code.widget.attrs.update({"style": "width: 20em;"})
