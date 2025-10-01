from django import forms


class RepeatChoreForm(forms.Form):
    chore = forms.CharField(
        label="Chore", max_length=100000, required=True)
    assign_to = forms.CharField(
        label="Assign to", max_length=100000, required=True)
    due_date = forms.DateField()
