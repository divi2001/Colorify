# apps\subscription_module\urls.py
from django.urls import path
from . import views

app_name = 'subscription_module'
urlpatterns = [
    path('subscribe/<int:plan_id>/', views.subscribe_user, name='subscribe_user'),
    path('subscription/success/', views.subscription_success, name='subscription_success'),
    path('premium/', views.premium_feature, name='premium_feature'),
    path('register/', views.register, name='register'),
    # path('paypal/', views.paypal_view, name='paypal_view'),
    # path('paypal/', include(paypal_urls)),
    path('admin/update_color/', views.update_color, name='update_color'),

    path('plans/', views.SubscriptionPlansView.as_view(), name='subscription_plans'),
    path('initiate-payment/<int:plan_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('validate-referral-code/', views.validate_referral_code, name='validate_referral_code')
]

