from django.contrib import messages
from django.shortcuts import redirect

from .subscription_access import PLANS_URL_NAME, user_has_active_plan


class RequireActivePlanMiddleware:
    """Redirect authenticated users without an active plan to the plans page."""

    EXEMPT_PREFIXES = (
        '/subscriptions/plans',
        '/subscriptions/initiate-payment',
        '/subscriptions/payment-callback',
        '/subscriptions/payment-success',
        '/subscriptions/validate-referral-code',
        '/accounts/',
        '/admin/',
    )

    EXEMPT_PATHS = {
        '/',
        '/about/',
        '/contact/',
        '/plans/',
        '/privacy-policy/',
        '/terms-of-service/',
        '/cancellation-policy/',
        '/shipping-policy/',
        '/affiliate/',
    }

    PUBLIC_CORE_PREFIXES = (
        '/core/contact-form-submission/',
        '/core/affiliate-form-submission/',
        '/core/newsletter-subscribe/',
        '/core/newsletter-unsubscribe/',
        '/core/check-username/',
        '/core/check-email/',
        '/core/reset-sessions-and-login/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not self._is_exempt(request.path):
            if not user_has_active_plan(request.user):
                messages.info(
                    request,
                    "Please choose a subscription plan to continue.",
                )
                return redirect(PLANS_URL_NAME)
        return self.get_response(request)

    def _is_exempt(self, path):
        if path in self.EXEMPT_PATHS:
            return True
        if path.startswith(self.EXEMPT_PREFIXES):
            return True
        if path.startswith(self.PUBLIC_CORE_PREFIXES):
            return True
        if path.startswith('/static/') or path.startswith('/media/'):
            return True
        return False
