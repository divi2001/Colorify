from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, F, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth, TruncWeek, ExtractMonth
from django.db import models
from apps.subscription_module.models import SubscriptionPlan, UserSubscription
from apps.core.models import CustomUser, Project
from django.contrib.auth import get_user_model
from django.db.models import Case, When, DecimalField
User = get_user_model()

@staff_member_required
def admin_dashboard(request):
    # Current date and time
    current_date = timezone.now()
    
    # Total Users
    total_users = User.objects.count()
    
    # New Users this month
    current_month_start = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_users_this_month = User.objects.filter(date_joined__gte=current_month_start).count()
    
    # Get monthly user registrations for the past 12 months
    twelve_months_ago = current_date - timedelta(days=365)
    monthly_registrations = User.objects.filter(
        date_joined__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('date_joined')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Subscription Analytics
    active_subscriptions = UserSubscription.objects.filter(
        end_date__gt=current_date,
        active=True
    )
    total_active_subscriptions = active_subscriptions.count()
    
    # Subscriptions by Plan
    subscriptions_by_plan = active_subscriptions.values(
        'plan__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Estimated Monthly Revenue (from active subscriptions)
    # Using discounted_price if available, otherwise original_price
    monthly_revenue_estimate = active_subscriptions.aggregate(
        revenue=Sum(
            Case(
                When(
                    plan__discounted_price__isnull=False,
                    then=F('plan__discounted_price') / (F('plan__duration_in_days') / 30)
                ),
                default=F('plan__original_price') / (F('plan__duration_in_days') / 30),
                output_field=models.DecimalField(),
            )
        )
    )['revenue'] or 0
    
    # Recent Subscriptions
    recent_subscriptions = UserSubscription.objects.all().order_by('-start_date')[:10]
    
    # User Projects Analytics
    total_projects = Project.objects.count()
    projects_by_status = Project.objects.values('status').annotate(count=Count('id'))

    # Subscription Expiry Analytics (Next 30 days)
    thirty_days_later = current_date + timedelta(days=30)
    expiring_soon = UserSubscription.objects.filter(
        end_date__gt=current_date,
        end_date__lte=thirty_days_later,
        active=True
    ).count()
    
    context = {
        'title': 'Analytics Dashboard',
        'total_users': total_users,
        'new_users_this_month': new_users_this_month,
        'monthly_registrations': list(monthly_registrations),
        'total_active_subscriptions': total_active_subscriptions,
        'subscriptions_by_plan': list(subscriptions_by_plan),
        'monthly_revenue_estimate': round(monthly_revenue_estimate, 2),
        'recent_subscriptions': recent_subscriptions,
        'total_projects': total_projects,
        'projects_by_status': list(projects_by_status),
        'expiring_soon': expiring_soon,
    }
    
    return render(request, 'admin/analytics_dashboard.html', context)