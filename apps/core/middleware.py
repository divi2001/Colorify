# apps/core/middleware.py
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.utils import timezone
from django.core.cache import cache
from django.shortcuts import render
from django.urls import reverse

class PreventConcurrentLoginsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            cache_key = f'user_session_{request.user.id}'
            current_session_key = request.session.session_key
            
            # Get stored session key from cache
            stored_session_key = cache.get(cache_key)
            
            if stored_session_key and stored_session_key != current_session_key:
                # Delete the current session
                Session.objects.filter(session_key=current_session_key).delete()
                logout(request)
                
                # Render the custom template
                return render(request, 'account/concurrent_login_error.html', {
                    'error_message': 'This account is already logged in on another device or browser. Please log out from other sessions to continue.'
                })
            
            # Store current session in cache
            cache.set(cache_key, current_session_key, timeout=None)
            
            # Update last activity
            cache.set(f'last_activity_{request.user.id}', timezone.now(), timeout=None)

        response = self.get_response(request)
        return response