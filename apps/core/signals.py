# apps/core/signals.py
from django.contrib.auth import user_logged_out
from django.core.cache import cache
from django.dispatch import receiver

@receiver(user_logged_out)
def remove_session_from_cache(sender, request, user, **kwargs):
    if user.is_authenticated:
        cache_key = f'user_sessions_{user.id}'
        current_session_key = request.session.session_key
        stored_sessions = cache.get(cache_key, [])
        
        if current_session_key in stored_sessions:
            stored_sessions.remove(current_session_key)
            cache.set(cache_key, stored_sessions, timeout=None)