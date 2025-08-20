# apps\subscription_module\admin.py
# This file contains the admin interface for managing subscription-related models in Django.
# It includes custom admin classes for SubscriptionPlan, UserSubscription, PaymentTransaction, Device,
# InspirationPDF, PDFLike, Palette, Color, and ReferralCode models.
# The admin interface allows for easy management of these models, including listing, filtering, and editing records.
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.http import JsonResponse
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .models import (
    SubscriptionPlan, UserSubscription, PaymentTransaction, Device,
    InspirationPDF, PDFLike, Palette, Color
)
from .utils import AutoPaletteGenerationForm
from .models import ReferralCode
from django.http import HttpResponseRedirect


# Custom admin classes for Subscription models
# This admin class manages the SubscriptionPlan model.
# It includes fields for displaying the plan name, type, current price, duration, and active status.
# It also allows filtering by subscription type and active status, and searching by name and description.
# The current price field is read-only to prevent accidental changes.
@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'subscription_type', 'current_price', 'duration_in_days', 'is_active')
    list_filter = ('subscription_type', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('current_price',)

    def current_price(self, obj):
        return obj.current_price
    current_price.short_description = 'Current Price'


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_active', 'start_date', 'end_date', 
                   'devices_used_count', 'get_max_devices', 'file_uploads_used', 'storage_used_mb')
    list_filter = ('active', 'plan')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)

    def is_active(self, obj):
        return obj.is_active()
    is_active.boolean = True
    is_active.short_description = 'Active'

    def get_max_devices(self, obj):
        return obj.plan.max_devices if obj.plan else None
    get_max_devices.short_description = 'Max Devices'

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'status', 'transaction_type', 'created_at')
    list_filter = ('status', 'transaction_type')
    search_fields = ('user__username', 'transaction_id')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_name', 'device_id', 'last_login', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'device_name', 'device_id')
    raw_id_fields = ('user',)

# Models for Inspiration PDFs
@admin.register(InspirationPDF)
class InspirationPDFAdmin(admin.ModelAdmin):
    list_display = ('title', 'likes_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title',)

@admin.register(PDFLike)
class PDFLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'pdf', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'pdf__title')

# Models for Color Palettes
class ColorAdminForm(forms.ModelForm):
    color_picker = forms.CharField(widget=forms.TextInput(attrs={'type': 'color', 'class': 'color-picker'}), required=False)

    class Meta:
        model = Color
        fields = ['red', 'green', 'blue', 'color_picker']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['color_picker'].initial = f'#{self.instance.red:02x}{self.instance.green:02x}{self.instance.blue:02x}'
        
        self.fields['red'].widget.attrs['class'] = 'rgb-input'
        self.fields['green'].widget.attrs['class'] = 'rgb-input'
        self.fields['blue'].widget.attrs['class'] = 'rgb-input'

class ColorInline(admin.TabularInline):
    model = Color
    form = ColorAdminForm
    extra = 0

class PaletteAdminForm(forms.ModelForm):
    base_color_picker = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color', 'class': 'color-picker'}),
        required=False
    )

    class Meta:
        model = Palette
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['num_colors'].widget.attrs['readonly'] = True
            self.fields['base_color_picker'].initial = f'#{self.instance.base_color_r:02x}{self.instance.base_color_g:02x}{self.instance.base_color_b:02x}'
        
        # Add classes to RGB inputs
        self.fields['base_color_r'].widget.attrs['class'] = 'rgb-input'
        self.fields['base_color_g'].widget.attrs['class'] = 'rgb-input'
        self.fields['base_color_b'].widget.attrs['class'] = 'rgb-input'

@admin.register(Palette)
class PaletteAdmin(admin.ModelAdmin):
    form = PaletteAdminForm
    list_display = ('name', 'creator', 'favorites_count', 'num_colors', 'display_base_color', 'type', 'created_at', 'updated_at', 'generate_palette_button')
    list_filter = ('created_at', 'updated_at', 'type')
    search_fields = ('name', 'creator__username', 'base_color')
    inlines = [ColorInline]

    def display_base_color(self, obj):
        return format_html(
            '<div style="background-color: rgb({}, {}, {}); width: 30px; height: 30px;"></div>',
            obj.base_color_r, obj.base_color_g, obj.base_color_b
        )
    display_base_color.short_description = 'Base Color'

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        for inline in inline_instances:
            if isinstance(inline, ColorInline):
                if obj:
                    inline.extra = obj.num_colors - obj.colors.count()
                else:
                    inline.extra = 5
        return inline_instances

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('base_color_picker'):
            color = form.cleaned_data['base_color_picker'].lstrip('#')
            obj.base_color_r = int(color[:2], 16)
            obj.base_color_g = int(color[2:4], 16)
            obj.base_color_b = int(color[4:], 16)
        
        super().save_model(request, obj, form, change)
        
        current_color_count = obj.colors.count()
        new_color_count = obj.num_colors

        if current_color_count < new_color_count:
            for _ in range(new_color_count - current_color_count):
                Color.objects.create(palette=obj, red=255, green=255, blue=255)
        elif current_color_count > new_color_count:
            obj.colors.order_by('-id')[:current_color_count - new_color_count].delete()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()
        
        form.instance.num_colors = form.instance.colors.count()
        form.instance.save()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate_palette/', self.generate_palette_view, name='generate_palette'),
            path('<int:palette_id>/update_colors/', self.update_colors_view, name='update_palette_colors'),
        ]
        return custom_urls + urls

    def update_colors_view(self, request, palette_id):
        palette = Palette.objects.get(id=palette_id)
        new_num_colors = int(request.POST.get('num_colors', palette.num_colors))
        current_color_count = palette.colors.count()

        if current_color_count < new_num_colors:
            for _ in range(new_num_colors - current_color_count):
                Color.objects.create(palette=palette, red=255, green=255, blue=255)
        elif current_color_count > new_num_colors:
            palette.colors.order_by('-id')[:current_color_count - new_num_colors].delete()

        palette.num_colors = new_num_colors
        palette.save()

        return JsonResponse({'status': 'success', 'new_num_colors': new_num_colors})

    def generate_palette_view(self, request):
        if request.method == 'POST':
            form = AutoPaletteGenerationForm(request.POST)
            if form.is_valid():
                num_palettes = int(request.POST.get('num_palettes', 1))
                palettes = []
                base_name = form.cleaned_data.get('name', 'Palette')
                
                for i in range(num_palettes):
                    # Create a new form instance for each palette
                    new_form_data = form.cleaned_data.copy()
                    if num_palettes > 1:
                        new_form_data['name'] = f"{base_name} {i+1}"
                    else:
                        new_form_data['name'] = base_name
                    new_form = AutoPaletteGenerationForm(new_form_data)
                    
                    if new_form.is_valid():
                        palette = new_form.generate_palette(user=request.user)
                        palettes.append(palette)
                
                if num_palettes == 1:
                    message = f"Palette '{palettes[0].name}' generated successfully."
                    return redirect('admin:subscription_module_palette_change', object_id=palettes[0].id)
                else:
                    message = f"{num_palettes} palettes generated successfully."
                
                self.message_user(request, message)
                return redirect('admin:subscription_module_palette_changelist')
            else:
                # If the form is not valid, we should handle the error
                self.message_user(request, "Error in form submission. Please check the inputs.", level='ERROR')
        else:
            form = AutoPaletteGenerationForm()

        context = {
            'form': form,
            'title': 'Generate Palette',
            'opts': self.model._meta,
        }
        return render(request, 'admin/generate_palette.html', context)

    def generate_palette_button(self, obj):
        url = reverse('admin:generate_palette')
        return format_html('<a class="button" href="{}">Generate Palette</a>', url)
    generate_palette_button.short_description = "Generate Palette"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['generate_palette_url'] = reverse('admin:generate_palette')
        return super().changelist_view(request, extra_context=extra_context)

    class Media:
        js = ('admin/js/jquery.min.js', 'admin/js/color_pickr.js', 'admin/js/palette_admin.js')
        css = {
            'all': ('admin/css/color_picker.css', 'admin/css/custom_admin.css')
        }

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    form = ColorAdminForm
    list_display = ('palette', 'display_color', 'red', 'green', 'blue')
    list_filter = ('palette',)

    def display_color(self, obj):
        return format_html(
            '<div style="background-color: rgb({}, {}, {}); width: 30px; height: 30px;"></div>',
            obj.red, obj.green, obj.blue
        )
    display_color.short_description = 'Color'

    class Media:
        js = (
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'admin/js/color_pickr.js',
        )
        css = {
            'all': ('admin/css/color_picker.css',)
        }

class ReferralCodeForm(forms.ModelForm):
    class Meta:
        model = ReferralCode
        fields = '__all__'

@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    form = ReferralCodeForm
    list_display = ('code', 'discount_percentage', 'is_active', 'current_uses', 'max_uses', 'expiration_date')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code',)
    filter_horizontal = ('applicable_plans',)
    readonly_fields = ('current_uses', 'created_at', 'generate_code_button')
    
    fieldsets = (
        (None, {
            'fields': ('generate_code_button', 'code', 'discount_percentage', 'is_active')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'current_uses', 'expiration_date')
        }),
        ('Applicability', {
            'fields': ('applicable_plans', 'created_by')
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def generate_code_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Generate Random Code</a>',
            reverse('admin:generate_referral_code')
        )
    generate_code_button.short_description = 'Generate Code'
    generate_code_button.allow_tags = True
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'generate-code/',
                self.admin_site.admin_view(self.generate_code),
                name='generate_referral_code'
            ),
        ]
        return custom_urls + urls
    
    def generate_code(self, request):
        if request.method == 'GET':
            new_code = ReferralCode.generate_random_code()
            return HttpResponseRedirect(
                reverse('admin:subscription_module_referralcode_add') + f'?code={new_code}'
            )
        return HttpResponseRedirect(reverse('admin:subscription_module_referralcode_add'))
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set created_by for new instances
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        if 'code' in request.GET:
            initial['code'] = request.GET['code']
        return initial