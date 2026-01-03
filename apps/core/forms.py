from django import forms
from allauth.account.forms import SignupForm as AllauthSignupForm
from .models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSignupForm(AllauthSignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose a different one.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already registered. Please use a different email or try logging in.')
        return email

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