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
            user_id = request.user.id
            cache_key = f'user_sessions_{user_id}'
            current_session_key = request.session.session_key
            
            # Get stored sessions from cache
            stored_sessions = cache.get(cache_key, [])
            
            # Clean up any expired sessions
            active_sessions = []
            for session_key in stored_sessions:
                if Session.objects.filter(session_key=session_key).exists():
                    active_sessions.append(session_key)
            
            # If current session is not in active sessions
            if current_session_key not in active_sessions:
                if len(active_sessions) >= self.MAX_SESSIONS:
                    # Delete the current session
                    Session.objects.filter(session_key=current_session_key).delete()
                    logout(request)
                    
                    # Render the custom template
                    return render(request, 'account/concurrent_login_error.html', {
                        'error_message': f'This account is already logged in on {self.MAX_SESSIONS} devices/browsers. Please log out from at least one session to continue.'
                    })
                
                # Add current session to active sessions
                active_sessions.append(current_session_key)
                cache.set(cache_key, active_sessions, timeout=None)
            else:
                # Update the cache with cleaned up sessions
                if len(active_sessions) != len(stored_sessions):
                    cache.set(cache_key, active_sessions, timeout=None)
            
            # Update last activity
            cache.set(f'last_activity_{user_id}', timezone.now(), timeout=None)

        response = self.get_response(request)
        return response