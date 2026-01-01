# apps/core/views/contact_views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.core.models import Contact, Affiliate
import json

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
            return JsonResponse({'status': 'error', 'message': 'An error occurred. Please try again.'})

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
            return JsonResponse({'status': 'error', 'message': 'An error occurred. Please try again.'})

    return render(request, 'pages/affiliate.html')