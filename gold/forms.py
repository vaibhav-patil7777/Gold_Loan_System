from django import forms
from .models import GoldItem

class GoldItemForm(forms.ModelForm):
    class Meta:
        model = GoldItem
        fields = '__all__'
