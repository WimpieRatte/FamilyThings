from django import forms
from finance.models import TransactionPattern

class TransactionPatternForm(forms.ModelForm):
    class Meta:
        model = TransactionPattern
        fields = ['business_entity_name', 'transaction_category_id']
        widgets = {
            'business_entity_name': forms.TextInput(attrs={'class': 'form-control'}),
            'transaction_category_id': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Here we can handle hidden/session specific fields
        self.family_id = kwargs.pop('family_id', None)
        super().__init__(*args, **kwargs)

        # If we're creating a new row and hidden values are provided, set it as initial
        if self.instance.pk is None and self.family_id:
            self.instance.family_id = self.family_id