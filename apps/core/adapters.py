from allauth.account.adapter import DefaultAccountAdapter
from django import forms

class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        email = super().clean_email(email)
        return email.lower()  # Store emails in lowercase