from django import forms


class UserRegisterForm(forms.Form):
    username = forms.CharField(
        label="User Name", max_length=24, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(
        label="Password", required=True,
        min_length=8,
        widget=forms.PasswordInput())
    first_name = forms.CharField(
        label="First Name", max_length=20, required=False)
    last_name = forms.CharField(
        label="Last Name", max_length=20, required=False)
    invite_code = forms.CharField(
        label="", max_length=50, required=False)

    invite_code.widget.attrs.update({"style": "width: 20em;"})
