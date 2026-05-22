from .subscription_access import get_subscription_alert


def subscription_alert(request):
    if not request.user.is_authenticated:
        return {'subscription_alert': None}
    return {'subscription_alert': get_subscription_alert(request.user)}
