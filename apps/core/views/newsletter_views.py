from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.core import signing
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from ..models import NewsletterSubscription
import json


def _build_unsubscribe_url(request, email):
    signer = signing.TimestampSigner()
    token = signer.sign(email)
    try:
        unsubscribe_path = reverse('newsletter-unsubscribe', kwargs={'token': token})
    except NoReverseMatch:
        # Fallback for environments where URL names are not refreshed yet.
        unsubscribe_path = f"/core/newsletter-unsubscribe/{token}/"
    return request.build_absolute_uri(unsubscribe_path)


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
            unsubscribe_url = _build_unsubscribe_url(request, email)
            try:
                send_mail(
                    'Welcome to Colorify Studio Newsletter',
                    (
                        "Hi,\n\n"
                        "Thank you for subscribing to the Colorify Studio newsletter.\n"
                        "You will now receive color trends, design tips, and special offers.\n\n"
                        f"Unsubscribe anytime: {unsubscribe_url}\n\n"
                        "Regards,\n"
                        "Colorify Studio Team"
                    ),
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=True,
                )
            except Exception:
                # Do not fail subscription if email sending has issues.
                pass
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
                unsubscribe_url = _build_unsubscribe_url(request, email)
                try:
                    send_mail(
                        'Your Colorify Newsletter Subscription Is Active Again',
                        (
                            "Hi,\n\n"
                            "Your newsletter subscription has been reactivated successfully.\n"
                            "You will continue receiving updates from Colorify Studio.\n\n"
                            f"Unsubscribe anytime: {unsubscribe_url}\n\n"
                            "Regards,\n"
                            "Colorify Studio Team"
                        ),
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                except Exception:
                    pass
                return JsonResponse({
                    'status': 'success',
                    'message': 'Welcome back! Your subscription has been reactivated.'
                })
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid request data'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def newsletter_unsubscribe(request, token):
    try:
        signer = signing.TimestampSigner()
        email = signer.unsign(token, max_age=60 * 60 * 24 * 30)  # 30 days

        subscription = NewsletterSubscription.objects.filter(email=email).first()
        if not subscription:
            return HttpResponse("Subscription not found.", status=404)

        if not subscription.is_active:
            return HttpResponse("You are already unsubscribed from the newsletter.", status=200)

        subscription.is_active = False
        subscription.save(update_fields=['is_active', 'updated_at'])
        return HttpResponse("You have been unsubscribed successfully.", status=200)
    except signing.BadSignature:
        return HttpResponse("Invalid unsubscribe link.", status=400)
    except signing.SignatureExpired:
        return HttpResponse("This unsubscribe link has expired.", status=400)
    except Exception:
        return HttpResponse("Unable to process unsubscribe request right now.", status=500)
