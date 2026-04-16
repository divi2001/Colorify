# apps/core/views/contact_views.py
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.utils import timezone
from apps.core.models import Contact, Affiliate
import json
import re
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def contact_form_submission(request):
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            phone_number = request.POST.get('phone_number', '')
            # Normalize phone before validation/save:
            # keep digits only and strip India country code if provided.
            phone_number = re.sub(r'\D', '', phone_number or '')
            if phone_number.startswith('91') and len(phone_number) > 10:
                phone_number = phone_number[2:]

            # Validate required fields
            if not all([first_name, last_name, email, subject, message]):
                return JsonResponse({'status': 'error', 'message': 'All required fields must be filled.'})

            # Create contact record
            contact = Contact(
                user=request.user if request.user.is_authenticated else None,
                first_name=first_name,
                last_name=last_name,
                email=email,
                subject=subject,
                message=message,
                phone_number=phone_number
            )
            contact.full_clean()
            contact.save()

            # Send email notification
            try:
                email_subject = f"New Contact Form Submission - {contact.get_subject_display()}"
                email_message = f"""
New contact form submission received:

Name: {first_name} {last_name}
Email: {email}
Phone: {phone_number or 'Not provided'}
Subject: {contact.get_subject_display()}

Message:
{message}

Submitted at: {contact.created_at}
"""
                
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    ['support@colorifystudio.ai'],  # Updated admin email
                    fail_silently=False,
                )
            except Exception as e:
                # Log email error but don't fail the form submission
                print(f"Email sending failed: {e}")

            return JsonResponse({'status': 'success', 'message': 'Your message has been sent successfully!'})
            
        except ValidationError as e:
            errors = [f"{field}: {error}" for field, errors in e.message_dict.items() for error in errors]
            return JsonResponse({'status': 'error', 'message': '; '.join(errors)})
        except Exception as e:
            logger.exception("Contact form submission failed")
            error_message = str(e) if settings.DEBUG else 'An error occurred. Please try again.'
            return JsonResponse({'status': 'error', 'message': error_message})

    return render(request, 'pages/contact.html')

@csrf_exempt
@require_http_methods(["GET", "POST"])
def affiliate_form_submission(request):
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            message = request.POST.get('message')
            phone_number = request.POST.get('phone_number', '')
            # Normalize phone before validation/save:
            # keep digits only and strip India country code if provided.
            phone_number = re.sub(r'\D', '', phone_number or '')
            if phone_number.startswith('91') and len(phone_number) > 10:
                phone_number = phone_number[2:]
            website_url = request.POST.get('website_url', '')
            social_media_followers = request.POST.get('social_media_followers', '')
            experience = request.POST.get('experience', '')

            # Validate required fields
            if not all([first_name, last_name, email, message]):
                return JsonResponse({'status': 'error', 'message': 'All required fields must be filled.'})

            # Create affiliate record
            affiliate = Affiliate(
                first_name=first_name,
                last_name=last_name,
                email=email,
                message=message,
                phone_number=phone_number,
                website_url=website_url,
                social_media_followers=social_media_followers,
                experience=experience
            )
            affiliate.full_clean()
            affiliate.save()

            # Send email notification
            try:
                email_subject = f"New Affiliate Application - {first_name} {last_name}"
                email_message = f"""
New affiliate application received:

Name: {first_name} {last_name}
Email: {email}
Phone: {phone_number or 'Not provided'}
Website: {website_url or 'Not provided'}
Social Media Followers: {social_media_followers or 'Not provided'}

Experience:
{experience or 'Not provided'}

Message:
{message}

Submitted at: {affiliate.created_at}
"""
                
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    ['affiliates@colorifystudio.ai'],  # Updated affiliate team email
                    fail_silently=False,
                )
            except Exception as e:
                # Log email error but don't fail the form submission
                print(f"Email sending failed: {e}")

            return JsonResponse({'status': 'success', 'message': 'Your affiliate application has been submitted successfully! We will review it and get back to you soon.'})
            
        except ValidationError as e:
            errors = [f"{field}: {error}" for field, errors in e.message_dict.items() for error in errors]
            return JsonResponse({'status': 'error', 'message': '; '.join(errors)})
        except Exception as e:
            logger.exception("Affiliate form submission failed")
            # Return actual exception text to quickly diagnose production failures.
            return JsonResponse({'status': 'error', 'message': f'Affiliate submit failed: {str(e)}'})

    return render(request, 'pages/affiliate.html')


@require_http_methods(["POST"])
def reset_sessions_and_continue_login(request):
    reset_token = request.POST.get('reset_token')
    if not reset_token:
        return redirect('account_login')

    cache_key = f'force_login_reset_{reset_token}'
    token_payload = cache.get(cache_key)
    if not token_payload:
        return redirect('account_login')

    user_id = token_payload.get('user_id')
    cache.delete(cache_key)
    if not user_id:
        return redirect('account_login')

    # Remove all active sessions for this user across devices/browsers.
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_sessions = []
    for session in sessions:
        auth_user_id = session.get_decoded().get('_auth_user_id')
        if str(auth_user_id) == str(user_id):
            user_sessions.append(session.session_key)

    if user_sessions:
        Session.objects.filter(session_key__in=user_sessions).delete()

    cache.set(f'user_sessions_{user_id}', [], timeout=None)

    # Keep subscription/device usage in sync after force logout-all.
    try:
        from apps.subscription_module.models import Device, UserSubscription

        Device.objects.filter(user_id=user_id, device_id__startswith='session_').update(is_active=False)
        subscription = UserSubscription.objects.filter(user_id=user_id).order_by('-id').first()
        if subscription:
            for device in subscription.devices.filter(device_id__startswith='session_'):
                subscription.devices.remove(device)
            subscription.devices_used_count = 0
            subscription.save(update_fields=['devices_used_count'])
    except Exception:
        # Do not block login flow if device cleanup fails.
        pass

    return redirect('account_login')