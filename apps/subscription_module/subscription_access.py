from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .models import UserSubscription

PLANS_URL_NAME = 'subscription_module:subscription_plans'
EXPIRING_SOON_DAYS = 7
RESOURCE_WARNING_PERCENT = 90
UNLIMITED_FILE_LIMIT = 2147483647
EXPORT_RESTRICTED_MESSAGE = (
    'Export is not available on the free trial plan. '
    'Please upgrade to a paid plan to export your files.'
)


def user_has_active_plan(user):
    """True when the user has an active subscription with a plan assigned."""
    if not user.is_authenticated:
        return False
    try:
        subscription = UserSubscription.objects.get(user=user)
    except UserSubscription.DoesNotExist:
        return False
    return bool(subscription.plan_id) and subscription.is_active()


def user_can_export(user):
    """Paid, non-trial subscribers can export files."""
    if not user.is_authenticated:
        return False

    try:
        subscription = UserSubscription.objects.select_related('plan').get(user=user)
    except UserSubscription.DoesNotExist:
        return False

    if not subscription.is_active() or not subscription.plan_id:
        return False

    plan = subscription.plan
    return not (plan.is_trial or plan.is_free)


def require_active_plan(request, message=None):
    """Redirect to the plans page when no active plan is assigned; otherwise None."""
    if user_has_active_plan(request.user):
        return None
    messages.info(
        request,
        message or "Please choose a subscription plan to continue.",
    )
    return redirect(PLANS_URL_NAME)


def _days_until_end(subscription):
    end = subscription.end_date
    if hasattr(end, 'date'):
        end = end.date()
    today = timezone.now().date()
    return max((end - today).days, 0)


def _usage_percent(used, limit):
    if limit <= 0:
        return 0
    return round((used / limit) * 100, 1)


def get_subscription_alert(user):
    """
    Build alert payload for subscription status popups.
    Returns None when no alert should be shown.
    """
    if not user.is_authenticated:
        return None

    plans_url = reverse(PLANS_URL_NAME)

    try:
        subscription = UserSubscription.objects.select_related('plan').get(user=user)
    except UserSubscription.DoesNotExist:
        return {
            'show': True,
            'type': 'no_plan',
            'severity': 'info',
            'title': 'Subscription Required',
            'message': 'Choose a subscription plan to unlock the full Colorify workspace.',
            'cta_url': plans_url,
            'cta_label': 'View Plans',
            'dismissible': False,
        }

    plan_name = subscription.get_effective_plan_name()

    if not subscription.plan_id:
        return {
            'show': True,
            'type': 'no_plan',
            'severity': 'info',
            'title': 'No Plan Assigned',
            'message': 'Subscribe to a plan to start uploading and editing your designs.',
            'cta_url': plans_url,
            'cta_label': 'View Plans',
            'dismissible': False,
        }

    if not subscription.is_active():
        return {
            'show': True,
            'type': 'expired',
            'severity': 'error',
            'title': 'Plan Expired',
            'message': (
                f'Your {plan_name} subscription has expired. '
                'Renew your plan to continue uploading files and using premium features.'
            ),
            'cta_url': plans_url,
            'cta_label': 'Renew Plan',
            'dismissible': False,
            'days_remaining': 0,
        }

    file_limit = subscription.get_effective_file_limit()
    files_used = subscription.file_uploads_used
    storage_limit = subscription.get_effective_storage_limit_mb()
    storage_used = subscription.storage_used_mb
    is_unlimited_files = file_limit >= UNLIMITED_FILE_LIMIT

    files_exhausted = not is_unlimited_files and files_used >= file_limit
    storage_exhausted = storage_limit > 0 and storage_used >= storage_limit

    if files_exhausted or storage_exhausted:
        parts = []
        if files_exhausted:
            parts.append(f'file uploads ({files_used}/{file_limit})')
        if storage_exhausted:
            parts.append(f'storage ({storage_used:.1f} MB / {storage_limit} MB)')
        return {
            'show': True,
            'type': 'resources_exhausted',
            'severity': 'error',
            'title': 'Resources Fully Used',
            'message': (
                f'You have reached your plan limit for {" and ".join(parts)}. '
                'Upgrade your plan to get more capacity.'
            ),
            'cta_url': plans_url,
            'cta_label': 'Upgrade Plan',
            'dismissible': False,
            'files_used': files_used,
            'file_limit': file_limit,
            'storage_used': round(storage_used, 1),
            'storage_limit': storage_limit,
            'files_used_percentage': _usage_percent(files_used, file_limit) if not is_unlimited_files else 0,
            'storage_used_percentage': _usage_percent(storage_used, storage_limit),
        }

    days_left = _days_until_end(subscription)
    if 0 < days_left <= EXPIRING_SOON_DAYS:
        day_word = 'day' if days_left == 1 else 'days'
        return {
            'show': True,
            'type': 'expiring_soon',
            'severity': 'warning',
            'title': 'Plan Expiring Soon',
            'message': (
                f'Your {plan_name} plan expires in {days_left} {day_word}. '
                'Renew now to avoid interruption.'
            ),
            'cta_url': plans_url,
            'cta_label': 'Renew Now',
            'dismissible': True,
            'days_remaining': days_left,
        }

    warnings = []
    if not is_unlimited_files and file_limit > 0:
        file_pct = _usage_percent(files_used, file_limit)
        if file_pct >= RESOURCE_WARNING_PERCENT:
            warnings.append(f'file uploads ({file_pct}% used)')

    if storage_limit > 0:
        storage_pct = _usage_percent(storage_used, storage_limit)
        if storage_pct >= RESOURCE_WARNING_PERCENT:
            warnings.append(f'storage ({storage_pct}% used)')

    if warnings:
        return {
            'show': True,
            'type': 'resources_warning',
            'severity': 'warning',
            'title': 'Resources Running Low',
            'message': (
                f'You are nearing your plan limits for {" and ".join(warnings)}. '
                'Consider upgrading before you run out.'
            ),
            'cta_url': plans_url,
            'cta_label': 'View Plans',
            'dismissible': True,
            'files_used': files_used,
            'file_limit': file_limit,
            'storage_used': round(storage_used, 1),
            'storage_limit': storage_limit,
            'files_used_percentage': _usage_percent(files_used, file_limit) if not is_unlimited_files else 0,
            'storage_used_percentage': _usage_percent(storage_used, storage_limit),
            'days_remaining': days_left,
        }

    return None
