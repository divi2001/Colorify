# apps/core/signals.py
from django.contrib.auth import user_logged_out
from django.core.cache import cache
from django.dispatch import receiver
from django.contrib.sessions.models import Session
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.core.cache import cache

@receiver(user_logged_out)
def remove_session_from_cache(sender, request, user, **kwargs):
    if user and user.is_authenticated:
        cache_key = f'user_sessions_{user.id}'
        current_session_key = request.session.session_key
        
        # Get all stored sessions
        stored_sessions = cache.get(cache_key, [])
        
        # Remove current session if it exists
        if current_session_key in stored_sessions:
            stored_sessions.remove(current_session_key)
            cache.set(cache_key, stored_sessions, timeout=None)
        
        # Also remove the session from database
        Session.objects.filter(session_key=current_session_key).delete()

@receiver(post_save, sender=get_user_model())
def clean_user_sessions(sender, instance, **kwargs):
    """Clean up expired sessions when user data changes"""
    cache_key = f'user_sessions_{instance.id}'
    stored_sessions = cache.get(cache_key, [])
    
    # Filter out expired sessions
    active_sessions = [
        s for s in stored_sessions 
        if Session.objects.filter(session_key=s).exists()
    ]
    
    if len(active_sessions) != len(stored_sessions):
        cache.set(cache_key, active_sessions, timeout=None)