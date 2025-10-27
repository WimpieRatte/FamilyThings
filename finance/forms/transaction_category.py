from django import forms
from finance.models import TransactionCategory

class TransactionCategoryForm(forms.ModelForm):
    class Meta:
        model = TransactionCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Here we can handle hidden/session specific fields
        self.family_id = kwargs.pop('family_id', None)
        super().__init__(*args, **kwargs)

        # If we're creating a new row and hidden values are provided, set it as initial
        if self.instance.pk is None and self.family_id:
            self.instance.family_id = self.family_id