from django import forms
from allauth.account.forms import SignupForm as AllauthSignupForm
from .models import CustomUser

class CustomSignupForm(AllauthSignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['gender', 'designation', 'phone_number', 'address_line', 'city', 'state', 'country']
        widgets = {
            'gender': forms.Select(choices=[('', 'Select Gender'), ('M', 'Male'), ('F', 'Female'), ('O', 'Other')]),
        }