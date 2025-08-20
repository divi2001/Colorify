# apps/subscription_module/views.py
import logging
from datetime import datetime, timedelta

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from paypal.standard.forms import PayPalPaymentsForm
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    SubscriptionPlan, UserSubscription, PaymentTransaction,
    ReferralCode, Color, Palette, PaletteFavorite
)
from .razorpay_utils import RazorpayConfig

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

class SubscriptionPlansView(LoginRequiredMixin, View):
    """View to display available subscription plans"""
    
    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('original_price')
        
        current_subscription = None
        try:
            current_subscription = UserSubscription.objects.get(user=request.user)
        except UserSubscription.DoesNotExist:
            pass
            
        context = {
            'plans': plans,
            'current_subscription': current_subscription,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,  # Pass to template
        }
        
        return render(request, 'subscription_module/plans.html', context)
    
    
@login_required
def initiate_payment(request, plan_id):
    print(f"DEBUG: initiate_payment called with plan_id: {plan_id}")

    """Initiate Razorpay payment for a subscription plan"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    # Check if user already has an active subscription
    try:
        existing_subscription = UserSubscription.objects.get(user=request.user)
        if existing_subscription.is_active():
            messages.warning(request, "You already have an active subscription.")
            return redirect('subscription_module:subscription_plans')
    except UserSubscription.DoesNotExist:
        pass
    
    # Calculate final amount (consider referral codes if needed)
    final_amount = plan.current_price
    referral_code = None
    
    # Handle referral code if provided
    referral_code_str = request.GET.get('referral_code')
    if referral_code_str:
        try:
            referral_code = ReferralCode.objects.get(
                code=referral_code_str.upper(),
                is_active=True
            )
            if referral_code.is_valid():
                if not referral_code.applicable_plans.exists() or plan in referral_code.applicable_plans.all():
                    final_amount = referral_code.apply_discount(final_amount)
                    messages.success(request, f"Referral code applied! {referral_code.discount_percentage}% discount")
                else:
                    messages.warning(request, "Referral code is not applicable for this plan")
                    referral_code = None
            else:
                messages.warning(request, "Referral code is expired or invalid")
                referral_code = None
        except ReferralCode.DoesNotExist:
            messages.warning(request, "Invalid referral code")
            referral_code = None
    
    # Create payment transaction
    transaction = PaymentTransaction.objects.create(
        user=request.user,
        subscription_plan=plan,
        amount=final_amount,
        referral_code=referral_code,
        status='pending'
    )
    
    # Create Razorpay order
    try:
        razorpay_config = RazorpayConfig()
        order = razorpay_config.create_order(
            amount=float(final_amount),
            receipt=f'txn_{transaction.transaction_id}',
            notes={
                'transaction_id': str(transaction.transaction_id),
                'user_id': request.user.id,
                'plan_id': plan_id
            }
        )
        
        # Store Razorpay order ID
        transaction.razorpay_order_id = order['id']
        transaction.save()
        
        context = {
            'order': order,
            'plan': plan,
            'transaction': transaction,
            'final_amount': final_amount,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'user': request.user,
        }
        
        return render(request, 'subscription_module/payment_checkout.html', context)
        
    except Exception as e:
        logger.error(f"Error creating Razorpay order: {e}")
        transaction.status = 'failed'
        transaction.save()
        messages.error(request, "Unable to initiate payment. Please try again.")
        return redirect('subscription_module:subscription_plans')

# Update your payment_callback view
@csrf_exempt
@require_POST
def payment_callback(request):
    """Handle Razorpay payment callback"""
    try:
        # Get payment details from POST data
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        final_amount = request.POST.get('final_amount')
        applied_referral_code = request.POST.get('applied_referral_code')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return JsonResponse({'status': 'error', 'message': 'Missing payment parameters'})
        
        # Find the transaction
        try:
            transaction = PaymentTransaction.objects.get(
                razorpay_order_id=razorpay_order_id,
                status='pending'
            )
        except PaymentTransaction.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Transaction not found'})
        
        # Verify payment signature
        razorpay_config = RazorpayConfig()
        if razorpay_config.verify_payment_signature(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        ):
            # Update transaction with final amount if referral code was applied
            if final_amount:
                transaction.amount = float(final_amount)
            
            # Update referral code if applied during checkout
            if applied_referral_code and not transaction.referral_code:
                try:
                    referral_code = ReferralCode.objects.get(
                        code=applied_referral_code.upper(),
                        is_active=True
                    )
                    if referral_code.is_valid():
                        transaction.referral_code = referral_code
                except ReferralCode.DoesNotExist:
                    pass  # Continue without referral code if not found
            
            # Payment verified successfully
            transaction.razorpay_payment_id = razorpay_payment_id
            transaction.razorpay_signature = razorpay_signature
            transaction.mark_as_completed(razorpay_payment_id)
            
            # Create or update subscription
            start_date = timezone.now()
            end_date = start_date + timezone.timedelta(days=transaction.subscription_plan.duration_in_days)
            
            UserSubscription.objects.update_or_create(
                user=transaction.user,
                defaults={
                    'plan': transaction.subscription_plan,
                    'start_date': start_date,
                    'end_date': end_date,
                    'active': True
                }
            )
            
            return JsonResponse({
                'status': 'success',
                'redirect_url': reverse('subscription_module:payment_success')
            })
        else:
            # Payment verification failed
            transaction.status = 'failed'
            transaction.save()
            return JsonResponse({'status': 'error', 'message': 'Payment verification failed'})
            
    except Exception as e:
        logger.error(f"Error in payment callback: {e}")
        return JsonResponse({'status': 'error', 'message': 'Payment processing failed'})

@login_required
def payment_success(request):
    """Payment success page"""
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        return render(request, 'subscription_module/payment_success.html', {
            'subscription': subscription
        })
    except UserSubscription.DoesNotExist:
        messages.error(request, "Subscription not found.")
        return redirect('subscription_module:subscription_plans')
    
# Add this to your views.py
@csrf_exempt
@login_required
def validate_referral_code(request):
    """Validate and apply referral code"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        import json
        data = json.loads(request.body)
        referral_code_str = data.get('referral_code', '').strip().upper()
        plan_id = data.get('plan_id')
        original_amount = float(data.get('original_amount', 0))
        
        if not referral_code_str:
            return JsonResponse({'success': False, 'message': 'Please enter a referral code'})
        
        try:
            referral_code = ReferralCode.objects.get(
                code=referral_code_str,
                is_active=True
            )
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
            
            if not referral_code.is_valid():
                return JsonResponse({
                    'success': False, 
                    'message': 'This referral code has expired or reached its usage limit'
                })
            
            # Check if code is applicable to this plan
            if (referral_code.applicable_plans.exists() and 
                not referral_code.applicable_plans.filter(id=plan.id).exists()):
                return JsonResponse({
                    'success': False, 
                    'message': 'This referral code is not valid for the selected plan'
                })
            
            # Calculate discounted amount
            discounted_amount = referral_code.apply_discount(original_amount)
            
            return JsonResponse({
                'success': True,
                'message': f'{referral_code.discount_percentage}% discount applied!',
                'discount_percentage': referral_code.discount_percentage,
                'discounted_amount': float(discounted_amount),
                'discount_amount': float(original_amount - discounted_amount)
            })
            
        except ReferralCode.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid referral code'})
        except SubscriptionPlan.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid subscription plan'})
            
    except Exception as e:
        logger.error(f"Error validating referral code: {e}")
        return JsonResponse({'success': False, 'message': 'Error processing referral code'})