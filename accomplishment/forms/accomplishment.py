from django import forms


class AccomplishmentForm(forms.Form):
    name = forms.CharField(
        label="Name", max_length=100, required=True)
    description = forms.CharField(label="Description", max_length=1000,
        widget=forms.Textarea, required=False)
    icon = forms.CharField(
        label="Icon", max_length=40, required=True)
    measurement = forms.IntegerField(
        label="Measurement", required=False)
    accomplishment_type = forms.ChoiceField(
        label="Type", required=False)
    is_achievement = forms.BooleanField(required=False)
    #  Used in case the user wants to repeat an existing one
    is_repeat = forms.BooleanField(required=False)

    # By default, Django creates a Textarea with 10 rows, which is too much.
    description.widget.attrs.update({"rows": "3"})

    # The icon selection is handled through the page's JavaScript
    icon.widget.attrs.update({"style": "display: none;"})
    is_repeat.widget.attrs.update({"style": "display: none;"})
