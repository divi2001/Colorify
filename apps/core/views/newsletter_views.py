from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from ..models import NewsletterSubscription
import json


@csrf_exempt
@require_http_methods(["POST"])
def newsletter_subscribe(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)
        
        # Try to create or get existing subscription
        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if created:
            return JsonResponse({
                'status': 'success',
                'message': 'Thank you for subscribing to our newsletter!'
            })
        else:
            if subscription.is_active:
                return JsonResponse({
                    'status': 'info',
                    'message': 'You are already subscribed to our newsletter!'
                })
            else:
                subscription.is_active = True
                subscription.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Welcome back! Your subscription has been reactivated.'
                })
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid request data'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
