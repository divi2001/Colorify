# apps\subscription_module\middleware.py
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import Device

class DeviceAuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Get device ID from request (you might need to adjust this based on your client)
        device_id = request.META.get('HTTP_X_DEVICE_ID') or request.session.get('device_id')
        
        if not device_id:
            return HttpResponseForbidden("Device identification required")
        
        # Check if device is registered and active
        device = Device.objects.filter(
            user=request.user,
            device_id=device_id,
            is_active=True
        ).first()
        
        if not device:
            # Check if user can add this device
            can_add, _ = request.user.can_add_device(device_id)
            if not can_add:
                return HttpResponseForbidden("Device limit reached. Please upgrade your subscription.")
            
            # Register new device
            Device.objects.create(
                user=request.user,
                device_id=device_id
            )
        else:
            # Update last login time
            device.last_login = timezone.now()
            device.save()
        
        return self.get_response(request)