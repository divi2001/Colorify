# apps/mainadmin/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from . import views

class DashboardAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(views.admin_dashboard), 
                 name='analytics_dashboard'),
        ]
        return custom_urls + urls
    
    # Override the changelist view to redirect to our dashboard
    def changelist_view(self, request, extra_context=None):
        # Redirect to the dashboard view
        return redirect('admin:analytics_dashboard')

# Register to a dummy model
from django.db import models

class DashboardModel(models.Model):
    """Dummy model for the dashboard."""
    title = models.CharField(max_length=100, default="Dashboard")
    
    class Meta:
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboard"
        app_label = 'mainadmin'
        
    def __str__(self):
        return self.title

admin.site.register(DashboardModel, DashboardAdmin)