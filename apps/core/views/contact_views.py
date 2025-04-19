from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from apps.core.models import Contact
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model

User = get_user_model()

@require_http_methods(["GET", "POST"])
@login_required
def contact_form_submission(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        phone_number = request.POST.get('phone_number', '')

        if email != request.user.email:
            return JsonResponse({'status': 'error', 'message': "The email address must match your account email."})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': "User with this email does not exist."})

        try:
            contact = Contact(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                subject=subject,
                message=message,
                phone_number=phone_number
            )
            contact.full_clean()
            contact.save()
            return JsonResponse({'status': 'success', 'message': "Your message has been sent successfully!"})
        except ValidationError as e:
            errors = [f"{field}: {error}" for field, errors in e.message_dict.items() for error in errors]
            return JsonResponse({'status': 'error', 'message': errors})

    return render(request, 'pages/contact.html')