from django import forms


class TransactionForm(forms.Form):
    name = forms.CharField(
        label="Name", max_length=200, required=True)
    description = forms.TextInput(
        label="Description", max_length=1000)
    amount = forms.DecimalField(
        label="Amount", required=True)
    currency = forms.CharField(
        label="Currency", max_length=3, required=True)
    date_of_transaction = forms.DateTimeField(
        label="Date of Transaction", required=True)
    reference = forms.CharField(
        label="Reference", max_length=200)
    business_entity = forms.IntegerField(
        label="Business Entity")

    # If the user creates a new Currency
    creates_currency = forms.BooleanField(
        label="Creates Currency", required=False)
    currency_description = forms.TextInput(
        label="Currency Description", max_length=1000)

    # If the user creates a new Business Entity
