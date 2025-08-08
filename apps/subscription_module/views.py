# apps/subscription_module/views.py
import logging
from django.shortcuts import render, redirect
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import SubscriptionPlan, UserSubscription
from datetime import timedelta
import stripe
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from paypal.standard.forms import PayPalPaymentsForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from .models import Color
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Palette, Color, PaletteFavorite
from datetime import datetime
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from .models import SubscriptionPlan, UserSubscription, PaymentTransaction
from .payu_utils import PayUConfig
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_favorite_palette(request):
    """
    Handles creation of favorite palettes with source image colors.
    """
    try:
        data = request.data
        
        print("🔴 FRONTEND SENT - Colors:", data.get('colors'))
        print("🔴 FRONTEND SENT - Source Colors:", data.get('source_image_colors'))
        
        # Get colors and source colors
        palette_colors_raw = data.get('colors', [])
        source_colors = data.get('source_image_colors', [])
        
        # Convert palette colors from dict format to array format
        palette_colors = []
        for color in palette_colors_raw:
            if isinstance(color, dict):
                # Handle dict format: {'red': 135, 'green': 138, 'blue': 120}
                r = color.get('red', 0)
                g = color.get('green', 0) 
                b = color.get('blue', 0)
                palette_colors.append([r, g, b])
            elif isinstance(color, list) and len(color) >= 3:
                # Handle array format: [135, 138, 120]
                palette_colors.append([color[0], color[1], color[2]])
            else:
                print(f"🔴 WARNING: Skipping invalid color format: {color}")
        
        print("🔴 CONVERTED PALETTE COLORS:", palette_colors)
        print("🔴 SOURCE COLORS (already arrays):", source_colors)
        
        if not palette_colors:
            return Response(
                {"error": "No valid colors provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the palette
        palette_name = data.get('name', f"Favorite Palette {now().strftime('%Y-%m-%d %H:%M')}")
        
        palette = Palette.objects.create(
            name=palette_name,
            creator=request.user,
            base_color="Generated",
            base_color_r=palette_colors[0][0],  # Now accessing array format
            base_color_g=palette_colors[0][1],
            base_color_b=palette_colors[0][2],
            num_colors=len(palette_colors),
            type=data.get('type', 'TR'),
            source_image_colors=source_colors  # Store source colors as-is (already arrays)
        )
        
        print("🔴 STORED IN DB - Source Colors:", palette.source_image_colors)
        
        # Create color records
        created_colors = []
        for color in palette_colors:
            color_obj = Color.objects.create(
                palette=palette,
                red=color[0],
                green=color[1],
                blue=color[2]
            )
            created_colors.append([color_obj.red, color_obj.green, color_obj.blue])
        
        print("🔴 CREATED COLOR OBJECTS:", created_colors)
        
        # Create favorite relationship
        favorite, created = PaletteFavorite.objects.get_or_create(
            user=request.user,
            palette=palette
        )
        
        palette.update_favorites_count()
        
        # Verify what we stored immediately
        retrieved_colors = list(palette.colors.all().values('red', 'green', 'blue'))
        print("🔴 IMMEDIATELY RETRIEVED FROM DB:", retrieved_colors)
        
        return Response({
            'success': True,
            'palette_id': palette.id,
            'favorites_count': palette.favorites_count,
            'is_favorite': True,
            'message': 'Palette successfully saved to favorites',
            'debug_info': {
                'stored_source_colors': palette.source_image_colors,
                'stored_palette_colors': retrieved_colors
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        import traceback
        print("🔴 FULL ERROR:", traceback.format_exc())
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_favorite_palette(request, palette_id):
    palette = get_object_or_404(Palette, id=palette_id)
    favorite = get_object_or_404(PaletteFavorite, user=request.user, palette=palette)
    favorite.delete()
    
    return Response({
        'message': 'Palette removed from favorites',
        'favorites_count': palette.favorites_count
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favorites(request):
    favorites = PaletteFavorite.objects.filter(user=request.user).select_related('palette')
    
    print(f"🟡 FOUND {favorites.count()} favorites for user {request.user.username}")
    
    data = []
    for favorite in favorites:
        palette = favorite.palette
        colors = palette.colors.all().values('red', 'green', 'blue')
        colors_list = list(colors)
        
        print(f"🟡 RETRIEVING - Palette '{palette.name}' (ID: {palette.id})")
        print(f"🟡 RETRIEVING - Source Colors: {palette.source_image_colors}")
        print(f"🟡 RETRIEVING - Palette Colors: {colors_list[:3]}... (showing first 3)")
        print(f"🟡 RETRIEVING - Total colors: {len(colors_list)}")
        
        data.append({
            'id': palette.id,
            'name': palette.name,
            'type': palette.type,
            'favorites_count': palette.favorites_count,
            'source_image_colors': palette.source_image_colors,
            'colors': colors_list
        })
    
    print(f"🟡 SENDING TO FRONTEND: {len(data)} palettes")
    if data:
        print(f"🟡 FIRST PALETTE PREVIEW: {data[0]['name']} with {len(data[0]['colors'])} colors")
    
    return Response(data)

@require_POST
@staff_member_required
def update_color(request):
    color_id = request.POST.get('color_id')
    red = request.POST.get('red')
    green = request.POST.get('green')
    blue = request.POST.get('blue')

    try:
        color = Color.objects.get(id=color_id)
        color.red = int(red)
        color.green = int(green)
        color.blue = int(blue)
        color.save()
        return JsonResponse({'success': True})
    except Color.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Color not found'})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid color values'})
    
    
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_free_trial(user):
    basic_plan = SubscriptionPlan.objects.get(name='Basic')
    UserSubscription.objects.create(
        user=user,
        plan=basic_plan,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=7),  # 7-day free trial
        active=True
    )

@login_required
def subscribe_user(request, plan_id):
    plan = SubscriptionPlan.objects.get(id=plan_id)
    if request.method == 'POST':
        token = request.POST['stripeToken']
        email = request.POST['stripeEmail']

        customer = stripe.Customer.create(email=email, source=token)
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': plan.price}],
        )

        # Save subscription data
        UserSubscription.objects.create(
            user=request.user,
            plan=plan,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=plan.duration_in_days),
            active=True
        )
        return redirect('subscription_success')

    return render(request, 'subscribe.html', {'plan': plan})

def subscription_success(request):
    return render(request, 'success.html')

@login_required
def premium_feature(request):
    subscription = UserSubscription.objects.get(user=request.user)
    if subscription.is_active() and subscription.plan.name == 'Premium':
        return render(request, 'premium_feature.html')
    return redirect('subscribe')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            create_free_trial(user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
@login_required
def access_premium_content(request):
    subscription = UserSubscription.objects.get(user=request.user)
    if subscription.is_active() and subscription.plan.name == 'Premium':
        return render(request, 'premium_content.html')
    return redirect('subscribe')


from .models import SubscriptionPlan, UserSubscription, PaymentTransaction
from .payu_utils import PayUConfig

# apps/subscription_module/views.py

# apps/subscription_module/views.py

# apps/subscription_module/views.py

class SubscriptionPlansView(LoginRequiredMixin, View):
    """View to display available subscription plans"""
    
    def get(self, request):
        # Debug: Check all plans first
        all_plans = SubscriptionPlan.objects.all()
        
        print(f"DEBUG: Total plans in database: {all_plans.count()}")
        
        for plan in all_plans:
            print(f"DEBUG: Plan - {plan.name}, Active: {plan.is_active}, Price: {plan.original_price}")
        
        # Fetch all plans for debugging
        plans = SubscriptionPlan.objects.all().order_by('original_price')
        
        print(f"DEBUG: Plans queryset count: {plans.count()}")
        
        current_subscription = None
        try:
            current_subscription = UserSubscription.objects.get(user=request.user)
        except UserSubscription.DoesNotExist:
            pass
            
        context = {
            'plans': plans,
            'current_subscription': current_subscription
        }
        
        # Use debug template temporarily
        return render(request, 'pages/plans_debug.html', context)
    
class InitiatePaymentView(LoginRequiredMixin, View):
    """Initiate payment process for subscription"""
    
    def get(self, request, plan_id):
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        
        # Create a pending transaction
        transaction = PaymentTransaction.objects.create(
            user=request.user,
            subscription_plan=plan,
            amount=plan.price,
            status='pending'
        )
        
        # Prepare PayU payment data
        payu = PayUConfig()
        txnid = str(transaction.transaction_id)
        
        # Basic user information
        firstname = request.user.first_name if request.user.first_name else request.user.username
        email = request.user.email
        phone = request.user.phone_number if hasattr(request.user, 'phone_number') else ''
        
        # Product information
        productinfo = f"Subscription: {plan.name}"
        
        # URLs
        success_url = request.build_absolute_uri(reverse('subscription_module:subscription_payment_success'))
        failure_url = request.build_absolute_uri(reverse('subscription_module:subscription_payment_failure'))

        # Prepare data dictionary for hash calculation
        data = {
            'key': payu.merchant_key,
            'txnid': txnid,
            'amount': str(plan.price),
            'productinfo': productinfo,
            'firstname': firstname,
            'email': email,
            'phone': phone,
            'surl': success_url,
            'furl': failure_url,
            'service_provider': 'payu_paisa',
            'udf1': str(transaction.id),  # Store transaction ID for reference
        }
        
        # Calculate hash
        data['hash'] = payu.calculate_hash(data)
        
        context = {
            'data': data,
            'plan': plan,
            'payu_url': payu.base_url,
            'transaction': transaction,
        }
        
        return render(request, 'subscription_module/initiate_payment.html', context)

class PaymentSuccessView(LoginRequiredMixin, View):
    """Handle successful payment callback from PayU"""
    
    def post(self, request):
        payu = PayUConfig()
        
        # Verify the hash to ensure the callback is authentic
        if not payu.verify_hash(request.POST):
            messages.error(request, "Invalid payment verification. Please contact support.")
            return redirect('subscription_plans')
        
        # Get transaction ID from the response
        transaction_id = request.POST.get('udf1')
        payu_reference = request.POST.get('mihpayid')
        status = request.POST.get('status')
        
        if status != 'success':
            messages.error(request, f"Payment failed with status: {status}")
            return redirect('subscription_plans')
        
        try:
            # Get and update transaction
            transaction = PaymentTransaction.objects.get(id=transaction_id)
            user_subscription = transaction.mark_as_completed(payu_reference)
            
            messages.success(request, f"Payment successful! Your subscription is active until {user_subscription.end_date.strftime('%d %b %Y')}.")
            return redirect('subscription_plans')
            
        except PaymentTransaction.DoesNotExist:
            messages.error(request, "Transaction not found. Please contact support.")
            return redirect('subscription_plans')

class PaymentFailureView(LoginRequiredMixin, View):
    """Handle failed payment callback from PayU"""
    
    def post(self, request):
        # Get error message from PayU
        error = request.POST.get('error', 'Payment failed')
        transaction_id = request.POST.get('udf1')
        
        try:
            # Update transaction status
            transaction = PaymentTransaction.objects.get(id=transaction_id)
            transaction.status = 'failed'
            transaction.save()
        except PaymentTransaction.DoesNotExist:
            pass
            
        messages.error(request, f"Payment failed: {error}")
        return redirect('subscription_plans')