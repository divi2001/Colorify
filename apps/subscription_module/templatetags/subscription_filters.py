# apps/subscription_module/templatetags/subscription_filters.py

from django import template

register = template.Library()

@register.filter
def currency_format(value):
    """Format currency values"""
    return f"₹{value:,.0f}"

@register.filter
def storage_format(mb_value):
    """Convert MB to human readable format"""
    if mb_value >= 2147483647:
        return "Unlimited"
    elif mb_value >= 1024:
        return f"{mb_value // 1024} GB"
    else:
        return f"{mb_value} MB"