from django import forms


class AccomplishmentForm(forms.Form):
    name = forms.CharField(
        label="Name", max_length=100, required=True)
    description = forms.TextInput(
        label="Description", max_length=1000)
    icon = forms.CharField(
        label="Icon", max_length=3, required=True)
    measurement = forms.IntegerField(
        label="Measurement")
