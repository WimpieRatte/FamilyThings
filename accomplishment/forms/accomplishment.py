from django import forms
from django.utils import timezone


class AccomplishmentForm(forms.Form):
    name = forms.CharField(
        label="Name", max_length=100, required=True)
    accomplishment_type = forms.CharField(
        label="Category", max_length=100, required=False)
    description = forms.CharField(label="Description", max_length=1000,
        widget=forms.Textarea, required=False)
    icon = forms.CharField(
        label="", max_length=40, required=True, widget=forms.HiddenInput())
    measurement = forms.CharField(max_length=4,
        label="Unit", required=False)
    measurement_quantity = forms.DecimalField(
        label="Value", required=False, min_value=0, widget=forms.NumberInput())
    timeframe = forms.BooleanField(
        label="Timeframe", required=False)
    date_from = forms.DateField(label="From", required=False, initial=timezone.now, widget=forms.DateInput())
    date_to = forms.DateField(label="To", required=False, initial=timezone.now, widget=forms.DateInput())
    date = forms.DateField(label="Cleared", required=False, initial=timezone.now, widget=forms.DateInput())
    is_achievement = forms.BooleanField(label="Spec. Achievement", required=False)
    #  Used in case the user wants to repeat an existing one
    is_repeat = forms.BooleanField(label="", required=False)

    # Link the widgets to the auto generated datalists (see constants.py for the elements)
    accomplishment_type.widget.attrs.update({"list": "type-suggestions", 'placeholder': 'Optional', "style": "width: 12em;"})
    measurement.widget.attrs.update({"list": "measurement-suggestions"})

    name.widget.attrs.update({"style": "width: 12em;"})

    # By default, Django creates a Textarea with 10 rows, which is too much.
    description.widget.attrs.update({"rows": "3", 'style': "width: 24em;", 'placeholder': 'Optional'})

    # Add Bootstrap classes to the fields
    is_achievement.widget.attrs.update({"class": "form-check-input", "style": "width: 32px; height: 32px; margin: 0;"})

    # Size tweaks for the measurement section
    measurement_quantity.widget.attrs.update({"style": "width: 5em; font-size: 1.15em;", 'placeholder': '0'})
    measurement.widget.attrs.update({"style": "width: 2.5em; font-size: 1.15em;", 'placeholder': 'x'})

    accomplishment_type.widget.attrs.update({"style": "width: 12em; height: 2em;"})

    # The icon selection is handled through the page's JavaScript
    icon.widget.attrs.update({"style": "display: none;"})
    is_repeat.widget.attrs.update({"style": "display: none;"})

    timeframe.widget.attrs.update({"class": "form-check-input"})
