# apps\subscription_module\forms.py
from django import forms
from django.core.validators import MinValueValidator

class UpgradeDeviceForm(forms.Form):
    additional_devices = forms.IntegerField(
        label="Number of additional devices",
        validators=[MinValueValidator(1)],
        initial=1,
        widget=forms.NumberInput(attrs={'min': 1})
    )