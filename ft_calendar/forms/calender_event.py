from django import forms
from django.utils import timezone


class CalendarEventForm(forms.Form):
    title = forms.CharField(
        label="Category", max_length=100, required=False)
    description = forms.CharField(label="Description", max_length=1000,
        widget=forms.Textarea, required=False)
    date = forms.DateField(label="From", required=False, initial=timezone.now, widget=forms.SelectDateWidget())

