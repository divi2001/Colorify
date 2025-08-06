# In your admin.py
from django.contrib import admin
from .models import Mockup

@admin.register(Mockup)
class MockupAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'has_base64_image', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['image_base64', 'image_type']
    
    def has_base64_image(self, obj):
        return bool(obj.image_base64)
    has_base64_image.boolean = True
    has_base64_image.short_description = 'Has Base64'
    
    def save_model(self, request, obj, form, change):
        # Automatically set created_by if not set
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)