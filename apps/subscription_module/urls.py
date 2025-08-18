# apps\subscription_module\urls.py
from django.urls import path
from . import views
from .views import (
    SubscriptionPlansView,
    InitiatePaymentView,
    PaymentSuccessView,
    PaymentFailureView
)

app_name = 'subscription_module'
urlpatterns = [
    path('subscribe/<int:plan_id>/', views.subscribe_user, name='subscribe_user'),
    path('subscription/success/', views.subscription_success, name='subscription_success'),
    path('premium/', views.premium_feature, name='premium_feature'),
    path('register/', views.register, name='register'),
    # path('paypal/', views.paypal_view, name='paypal_view'),
    # path('paypal/', include(paypal_urls)),
    path('admin/update_color/', views.update_color, name='update_color'),

    path('plans/', SubscriptionPlansView.as_view(), name='subscription_plans'),
    path('payment/initiate/<int:plan_id>/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('payment/success/', PaymentSuccessView.as_view(), name='subscription_payment_success'),
    path('payment/failure/', PaymentFailureView.as_view(), name='subscription_payment_failure'),
]

