from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
import csv
from .models import Contact, CustomUser, NewsletterSubscription, Affiliate

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'subject', 'created_at')
    list_filter = ('subject', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'message')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-excel/', self.export_excel, name='core_contact_export_excel'),
        ]
        return custom_urls + urls
    
    def export_excel(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contacts.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Subject', 'Message', 'Created At'])
        
        contacts = Contact.objects.all()
        for contact in contacts:
            writer.writerow([
                contact.first_name,
                contact.last_name,
                contact.email,
                contact.phone_number or '',
                contact.get_subject_display(),
                contact.message,
                contact.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('display_username', 'email', 'full_name', 'gender', 'designation', 'phone_number', 'date_joined')
    list_filter = ('gender', 'designation', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'gender', 'designation', 'phone_number', 'profile_photo')}),
        ('Address', {'fields': ('address_line', 'city', 'state', 'country')}),
        ('Company Details', {'fields': ('company_name', 'company_website', 'company_size', 'company_industry', 'tax_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    def display_username(self, obj):
        """Display username with @ symbol"""
        return f"@{obj.username}"
    display_username.short_description = 'Username'
    display_username.admin_order_field = 'username'
    
    def full_name(self, obj):
        """Display full name or username if name not set"""
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return f"@{obj.username}"
    full_name.short_description = 'Full Name'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-excel/', self.export_excel, name='core_customuser_export_excel'),
        ]
        return custom_urls + urls
    
    def export_excel(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Gender', 'Designation', 'Phone', 'Address', 'City', 'State', 'Country', 'Company Name', 'Company Website', 'Company Size', 'Company Industry', 'Tax ID', 'Date Joined'])
        
        users = CustomUser.objects.all()
        for user in users:
            writer.writerow([
                user.username,
                user.email,
                user.first_name or '',
                user.last_name or '',
                user.get_gender_display() if user.gender else '',
                user.designation or '',
                user.phone_number or '',
                user.address_line or '',
                user.city or '',
                user.state or '',
                user.country or '',
                user.company_name or '',
                user.company_website or '',
                user.get_company_size_display() if user.company_size else '',
                user.company_industry or '',
                user.tax_id or '',
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at', 'updated_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-excel/', self.export_excel, name='core_newslettersubscription_export_excel'),
        ]
        return custom_urls + urls
    
    def export_excel(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="newsletter_subscriptions.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'Status', 'Subscribed At', 'Updated At'])
        
        subscriptions = NewsletterSubscription.objects.all()
        for subscription in subscriptions:
            writer.writerow([
                subscription.email,
                'Active' if subscription.is_active else 'Inactive',
                subscription.subscribed_at.strftime('%Y-%m-%d %H:%M:%S'),
                subscription.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
@admin.register(Affiliate)
class AffiliateAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('created_at',)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-excel/', self.export_excel, name='core_affiliate_export_excel'),
        ]
        return custom_urls + urls
    
    def export_excel(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="affiliates.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Website', 'Social Media Followers', 'Experience', 'Message', 'Status', 'Created At'])
        
        affiliates = Affiliate.objects.all()
        for affiliate in affiliates:
            writer.writerow([
                affiliate.first_name,
                affiliate.last_name,
                affiliate.email,
                affiliate.phone_number or '',
                affiliate.website_url or '',
                affiliate.social_media_followers or '',
                affiliate.experience or '',
                affiliate.message,
                affiliate.get_status_display(),
                affiliate.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response