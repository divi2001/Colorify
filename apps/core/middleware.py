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
        self.MAX_SESSIONS = 3  # Maximum allowed concurrent sessions

    def __call__(self, request):
        if request.user.is_authenticated:
            cache_key = f'user_sessions_{request.user.id}'
            current_session_key = request.session.session_key
            
            # Get stored sessions from cache
            stored_sessions = cache.get(cache_key, [])
            
            # If current session is not in stored sessions
            if current_session_key not in stored_sessions:
                if len(stored_sessions) >= self.MAX_SESSIONS:
                    # Delete the current session
                    Session.objects.filter(session_key=current_session_key).delete()
                    logout(request)
                    
                    # Render the custom template
                    return render(request, 'account/concurrent_login_error.html', {
                        'error_message': f'This account is already logged in on {self.MAX_SESSIONS} devices/browsers. Please log out from at least one session to continue.'
                    })
                
                # Add current session to stored sessions
                stored_sessions.append(current_session_key)
                cache.set(cache_key, stored_sessions, timeout=None)
            
            # Update last activity
            cache.set(f'last_activity_{request.user.id}', timezone.now(), timeout=None)

        response = self.get_response(request)
        return response