# apps/core/signals.py
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.core.cache import cache

@receiver(user_logged_out)
def clear_session_on_logout(sender, user, request, **kwargs):
    if user:
        cache.delete(f'user_session_{user.id}')
        cache.delete(f'last_activity_{user.id}')