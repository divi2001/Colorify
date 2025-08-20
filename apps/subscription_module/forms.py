# apps\subscription_module\forms.py
# This file contains forms related to subscription management, including upgrading devices and applying referral codes.
# It uses Django's forms framework to create and validate user input for these actions.
from django import forms
from django.core.validators import MinValueValidator
from django import forms
from .models import ReferralCode, SubscriptionPlan

# This form is used to upgrade the number of devices a user can use under their subscription.
# It includes a field for the number of additional devices, which must be at least 1.
# The initial value is set to 1, and the widget is a number input with a minimum value of 1.
class UpgradeDeviceForm(forms.Form):
    additional_devices = forms.IntegerField(
        label="Number of additional devices",
        validators=[MinValueValidator(1)],
        initial=1,
        widget=forms.NumberInput(attrs={'min': 1})
    )

# This form is used to apply a referral code when subscribing to a plan.
# It includes a field for the referral code and a hidden field for the plan ID.
# The clean method checks if the referral code is valid and applicable to the selected plan.
# If valid, it calculates the discounted price based on the referral code's discount percentage.
class ReferralCodeForm(forms.Form):
    code = forms.CharField(max_length=20)
    plan_id = forms.IntegerField(widget=forms.HiddenInput())
    
    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        plan_id = cleaned_data.get('plan_id')
        
        try:
            referral_code = ReferralCode.objects.get(code=code)
            plan = SubscriptionPlan.objects.get(id=plan_id)
            
            if not referral_code.is_valid():
                raise forms.ValidationError("This referral code is no longer valid.")
                
            if (referral_code.applicable_plans.exists() and 
                not referral_code.applicable_plans.filter(id=plan.id).exists()):
                raise forms.ValidationError("This referral code is not valid for the selected plan.")
                
            cleaned_data['referral_code'] = referral_code
            cleaned_data['discounted_price'] = referral_code.apply_discount(plan.current_price)
            
        except ReferralCode.DoesNotExist:
            raise forms.ValidationError("Invalid referral code.")
        except SubscriptionPlan.DoesNotExist:
            raise forms.ValidationError("Invalid subscription plan.")
            
        return cleaned_data
    
