# apps/core/middleware.py
from django.contrib.sessions.models import Session
from django.contrib.auth import logout, signals as auth_signals
from django.utils import timezone
from django.core.cache import cache
from django.shortcuts import render
from django.urls import reverse
from django.db import transaction
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

# Register a signal handler to handle logout events
@receiver(auth_signals.user_logged_out)
def handle_user_logout(sender, request, user, **kwargs):
    """
    Handle user logout by removing the session from active sessions
    and updating the device count.
    """
    if user and request and request.session.session_key:
        try:
            # Get cache key and current session
            user_id = user.id
            cache_key = f'user_sessions_{user_id}'
            current_session_key = request.session.session_key
            
            # Get stored sessions from cache
            stored_sessions = cache.get(cache_key, [])
            
            # Remove current session if it exists
            if current_session_key in stored_sessions:
                stored_sessions.remove(current_session_key)
                cache.set(cache_key, stored_sessions, timeout=None)
                logger.info(f"Removed session {current_session_key} from user {user_id} active sessions on logout")
            
            # Update the subscription's devices and count
            try:
                if hasattr(user, 'subscription'):
                    subscription = user.subscription
                    
                    # Remove device from subscription
                    from apps.subscription_module.models import Device
                    device_id = f"session_{current_session_key}"
                    
                    with transaction.atomic():
                        # Try to get the device
                        device = Device.objects.filter(
                            user=user,
                            device_id=device_id
                        ).first()
                        
                        if device:
                            # Remove from subscription's devices
                            if device in subscription.devices.all():
                                subscription.devices.remove(device)
                                
                            # Mark as inactive
                            device.is_active = False
                            device.save(update_fields=['is_active'])
                            
                            # Update count based on remaining active sessions
                            active_sessions = []
                            for session_key in stored_sessions:
                                if Session.objects.filter(session_key=session_key).exists():
                                    active_sessions.append(session_key)
                            
                            # Update subscription device count
                            subscription.devices_used_count = len(active_sessions)
                            subscription.save(update_fields=['devices_used_count'])
                            
                            logger.info(f"Updated device count for user {user_id} to {len(active_sessions)} after logout")
            except Exception as e:
                logger.error(f"Error updating subscription on logout: {str(e)}", exc_info=True)
                
        except Exception as e:
            logger.error(f"Error handling user logout: {str(e)}", exc_info=True)


class PreventConcurrentLoginsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.DEFAULT_MAX_SESSIONS = 1  # Default fallback if no subscription found

    def __call__(self, request):
        if request.user.is_authenticated:
            user_id = request.user.id
            cache_key = f'user_sessions_{user_id}'
            current_session_key = request.session.session_key
            
            # Get user subscription and max sessions limit
            subscription, max_sessions = self.get_user_subscription(request.user)
            
            # Get stored sessions from cache
            stored_sessions = cache.get(cache_key, [])
            
            # Clean up any expired sessions
            active_sessions = []
            for session_key in stored_sessions:
                if Session.objects.filter(session_key=session_key).exists():
                    active_sessions.append(session_key)
            
            # If current session is not in active sessions
            if current_session_key not in active_sessions:
                # Check if adding this session would exceed the limit
                if len(active_sessions) >= max_sessions:
                    # Delete the current session
                    Session.objects.filter(session_key=current_session_key).delete()
                    logout(request)
                    
                    # Render the custom template
                    return render(request, 'account/concurrent_login_error.html', {
                        'error_message': f'This account is already logged in on {max_sessions} devices/browsers. Please log out from at least one session to continue.'
                    })
                
                # Add current session to active sessions
                active_sessions.append(current_session_key)
                cache.set(cache_key, active_sessions, timeout=None)
                
                # Create or update device record
                if subscription:
                    self.record_device(subscription, current_session_key)
            else:
                # Update the cache with cleaned up sessions
                if len(active_sessions) != len(stored_sessions):
                    cache.set(cache_key, active_sessions, timeout=None)
            
            # Ensure subscription devices_used_count matches active sessions
            if subscription and len(active_sessions) != subscription.devices_used_count:
                self.synchronize_device_count(subscription, active_sessions)
            
            # Update last activity
            cache.set(f'last_activity_{user_id}', timezone.now(), timeout=None)

        response = self.get_response(request)
        return response
    
    def get_user_subscription(self, user):
        """Get user subscription and max sessions limit."""
        try:
            # Import here to avoid circular imports
            from apps.subscription_module.models import SubscriptionPlan, UserSubscription
            from django.core.exceptions import ObjectDoesNotExist
            
            # Try to get existing subscription
            try:
                subscription = user.subscription
                if subscription and subscription.plan:
                    # Check if subscription is active
                    if subscription.is_active():
                        return subscription, subscription.plan.max_devices
                    else:
                        # If subscription has expired, renew it with default plan
                        return self.create_or_renew_subscription(user)
                else:
                    # If subscription exists but has no plan, update it
                    return self.create_or_renew_subscription(user, subscription)
            except (AttributeError, ObjectDoesNotExist):
                # If no subscription exists, create one
                return self.create_or_renew_subscription(user)
            
        except Exception as e:
            logger.error(f"Error in get_user_subscription: {str(e)}", exc_info=True)
        
        return None, self.DEFAULT_MAX_SESSIONS
    
    def create_or_renew_subscription(self, user, existing_subscription=None):
        """Create a new subscription or renew an existing one with the default plan."""
        try:
            # Import here to avoid circular imports
            from apps.subscription_module.models import SubscriptionPlan, UserSubscription
            
            # Get the default plan
            try:
                default_plan = SubscriptionPlan.objects.get(name="Legacy Default Plan")
            except SubscriptionPlan.DoesNotExist:
                logger.error(f"Legacy Default Plan does not exist in the database.")
                return None, self.DEFAULT_MAX_SESSIONS
            
            start_date = timezone.now()
            end_date = start_date + timezone.timedelta(days=default_plan.duration_in_days)
            
            with transaction.atomic():
                if existing_subscription:
                    # Update existing subscription
                    existing_subscription.plan = default_plan
                    existing_subscription.start_date = start_date
                    existing_subscription.end_date = end_date
                    existing_subscription.active = True
                    existing_subscription.save()
                    subscription = existing_subscription
                else:
                    # Create new subscription
                    subscription = UserSubscription.objects.create(
                        user=user,
                        plan=default_plan,
                        start_date=start_date,
                        end_date=end_date,
                        active=True,
                        devices_used_count=0  # Start with 0
                    )
                
                logger.info(f"Created/renewed subscription for user {user.id} with plan {default_plan.name}")
                return subscription, default_plan.max_devices
                
        except Exception as e:
            logger.error(f"Error creating or renewing subscription: {str(e)}", exc_info=True)
            return None, self.DEFAULT_MAX_SESSIONS
    
    def record_device(self, subscription, session_key):
        """Record session as a device in the database."""
        try:
            from apps.subscription_module.models import Device
            
            # Create a unique device ID from the session key
            device_id = f"session_{session_key}"
            
            # Create or get device
            with transaction.atomic():
                device, created = Device.objects.get_or_create(
                    user=subscription.user,
                    device_id=device_id,
                    defaults={
                        'device_name': f"Browser Session ({timezone.now().strftime('%Y-%m-%d')})",
                        'is_active': True
                    }
                )
                
                # If device exists but is marked inactive, reactivate it
                if not created and not device.is_active:
                    device.is_active = True
                    device.last_login = timezone.now()
                    device.save(update_fields=['is_active', 'last_login'])
                    logger.info(f"Reactivated device for user {subscription.user.id}: {device_id}")
                
                # Add to subscription's devices if not already there
                if device not in subscription.devices.all():
                    subscription.devices.add(device)
                
                if created:
                    logger.info(f"Created new device for user {subscription.user.id}: {device_id}")
                    
            return device
        except Exception as e:
            logger.error(f"Error recording device: {str(e)}", exc_info=True)
            return None
    
    def synchronize_device_count(self, subscription, active_sessions):
        """Ensure the devices_used_count matches the actual number of active sessions."""
        try:
            from apps.subscription_module.models import Device
            
            # Get all device IDs for active sessions
            active_device_ids = [f"session_{session_key}" for session_key in active_sessions]
            
            with transaction.atomic():
                # Update devices_used_count to match active sessions
                old_count = subscription.devices_used_count
                subscription.devices_used_count = len(active_sessions)
                subscription.save(update_fields=['devices_used_count'])
                
                if old_count != len(active_sessions):
                    logger.info(f"Updated device count for user {subscription.user.id} from {old_count} to {len(active_sessions)}")
                
                # Clean up devices in the subscription that don't have active sessions
                all_devices = subscription.devices.all()
                for device in all_devices:
                    if device.device_id not in active_device_ids and device.device_id.startswith('session_'):
                        subscription.devices.remove(device)
                        device.is_active = False
                        device.save(update_fields=['is_active'])
                        logger.info(f"Removed inactive device {device.device_id} from user {subscription.user.id}")
                
                # Ensure all session devices are in the subscription
                for device_id in active_device_ids:
                    device = Device.objects.filter(device_id=device_id, user=subscription.user).first()
                    if device and device not in subscription.devices.all():
                        subscription.devices.add(device)
                        logger.info(f"Added missing device {device_id} to user {subscription.user.id} subscription")
        
        except Exception as e:
            logger.error(f"Error synchronizing device count: {str(e)}", exc_info=True)