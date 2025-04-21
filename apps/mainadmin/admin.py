# apps/mainadmin/admin.py
from django.contrib import admin
from django.urls import path
from . import views

# This is the key part - we're extending the AdminSite get_urls method
class DashboardAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', views.admin_dashboard, name='analytics_dashboard'),
        ]
        return custom_urls + urls

# Register to a dummy model (you can create a simple one if needed)
# For example:
from django.db import models

class DashboardModel(models.Model):
    """Dummy model for the dashboard."""
    class Meta:
        verbose_name_plural = "Dashboard"
        app_label = 'mainadmin'

admin.site.register(DashboardModel, DashboardAdmin)