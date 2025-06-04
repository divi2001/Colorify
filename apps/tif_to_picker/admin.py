from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Mockup

@admin.register(Mockup)
class MockupAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'created_by']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']