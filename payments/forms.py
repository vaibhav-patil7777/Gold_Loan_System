from django import forms
from .models import Payment
from loans.models import Loan

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['loan', 'amount_paid']

    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer', None)  # current customer pass karenge
        super().__init__(*args, **kwargs)

        if customer:
            # Sirf us customer ke loans hi dikhao
            self.fields['loan'].queryset = Loan.objects.filter(customer=customer)
