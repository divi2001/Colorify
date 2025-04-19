from django.contrib import admin
from .models import Contact, CustomUser

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'subject', 'created_at')
    list_filter = ('subject', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'message')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'gender', 'designation', 'phone_number')
    list_filter = ('gender', 'designation')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'gender', 'designation', 'phone_number')}),
        ('Address', {'fields': ('address_line', 'city', 'state', 'country')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )