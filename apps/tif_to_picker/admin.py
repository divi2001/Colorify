# In your admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Mockup

@admin.register(Mockup)
class MockupAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'has_base64_image', 'image_preview', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['image_preview_large', 'image_base64_info']
    
    def has_base64_image(self, obj):
        return bool(obj.image_base64)
    has_base64_image.boolean = True
    has_base64_image.short_description = 'Has Base64'
    
    def image_preview(self, obj):
        if obj.image_base64:
            return format_html(
                '<img src="data:{};base64,{}" style="max-width: 50px; max-height: 50px;" />',
                obj.image_type,
                obj.image_base64[:100] + '...'  # Truncate for performance
            )
        return "No image"
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        if obj.image_base64:
            return format_html(
                '<img src="data:{};base64,{}" style="max-width: 200px; max-height: 200px;" />',
                obj.image_type,
                obj.image_base64
            )
        return "No image"
    image_preview_large.short_description = 'Image Preview'
    
    def image_base64_info(self, obj):
        if obj.image_base64:
            size_kb = len(obj.image_base64) * 3 / 4 / 1024  # Approximate size in KB
            return f"Type: {obj.image_type}, Size: ~{size_kb:.1f} KB"
        return "No base64 data"
    image_base64_info.short_description = 'Base64 Info'
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)