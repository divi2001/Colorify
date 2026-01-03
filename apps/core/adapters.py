"""
Custom Django-allauth adapters for Colorify Studio
"""
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter to handle case-insensitive email and username login
    """
    
    def authenticate(self, request, **credentials):
        """
        Override authenticate to handle case-insensitive login
        """
        from django.contrib.auth import authenticate
        
        # Get the login identifier (could be email or username)
        login = credentials.get('username')  # allauth uses 'username' key for login field
        password = credentials.get('password')
        
        if not login or not password:
            return None
        
        # Try to authenticate with the original value first
        user = authenticate(request, username=login, password=password)
        
        if user:
            return user
        
        # If direct authentication fails, try case-insensitive email lookup
        if '@' in login:
            # It's an email - try case-insensitive lookup
            try:
                user_obj = User.objects.get(email__iexact=login)
                # Now try to authenticate with the actual username
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    return user
            except User.DoesNotExist:
                pass
            except User.MultipleObjectsReturned:
                # If multiple users with same email (shouldn't happen), use first one
                user_obj = User.objects.filter(email__iexact=login).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)
                    if user:
                        return user
        else:
            # It's a username - try case-insensitive lookup
            try:
                user_obj = User.objects.get(username__iexact=login)
                # Now try to authenticate with the actual username
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    return user
            except User.DoesNotExist:
                pass
            except User.MultipleObjectsReturned:
                # If multiple users with same username (shouldn't happen), use first one
                user_obj = User.objects.filter(username__iexact=login).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)
                    if user:
                        return user
        
        return None
    
    def is_email_verified(self, request, email):
        """
        Check if email is verified
        """
        from allauth.account.models import EmailAddress
        
        try:
            email_address = EmailAddress.objects.get(email__iexact=email, verified=True)
            return True
        except EmailAddress.DoesNotExist:
            return False
    
    def clean_email(self, email):
        """
        Normalize email to lowercase for consistency
        """
        return email.lower().strip() if email else email
    
    def clean_username(self, username, shallow=False):
        """
        Clean and validate username
        """
        username = super().clean_username(username, shallow=shallow)
        return username.lower().strip() if username else username
    
    def send_mail(self, template_prefix, email, context):
        """
        Override to send HTML emails with plain text fallback
        """
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        
        # Get subject
        subject = render_to_string(f'{template_prefix}_subject.txt', context)
        subject = " ".join(subject.splitlines()).strip()
        
        # Get plain text body
        text_body = render_to_string(f'{template_prefix}_message.txt', context)
        
        # Create email
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=self.get_from_email(),
            to=[email]
        )
        
        # Try to attach HTML version
        try:
            html_body = render_to_string(f'{template_prefix}_message.html', context)
            msg.attach_alternative(html_body, "text/html")
        except Exception:
            # If HTML template doesn't exist, just send plain text
            pass
        
        msg.send()
        return True
