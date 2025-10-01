from django import forms


class ChoreForm(forms.Form):
    name = forms.CharField(
        label="Name", max_length=100, required=True)
    description = forms.TextInput(
        label="Description", max_length=1000)
    icon = forms.CharField(
        label="Icon", max_length=3, required=True)
    assign_to = forms.CharField(
        label="Assign to", max_length=100000, required=True)
    due_date = forms.DateField()
