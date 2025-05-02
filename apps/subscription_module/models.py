# apps\subscription_module\models.py
from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator,MinValueValidator,MaxValueValidator
from django.utils import timezone
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class SubscriptionPlan(models.Model):
    SUBSCRIPTION_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom')
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    subscription_type = models.CharField(
        max_length=20, 
        choices=SUBSCRIPTION_TYPE_CHOICES,
        default='monthly'
    )
    duration_in_days = models.IntegerField(
        help_text="Total duration in days for the subscription"
    )
    original_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Full price of the subscription"
    )
    discounted_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True, 
        blank=True,
        help_text="Discounted price if available"
    )
    file_upload_limit = models.IntegerField(
        default=10,
        help_text="Number of files user can upload"
    )
    storage_limit_mb = models.IntegerField(
        default=1024,  # 1GB default
        help_text="Storage limit in MB"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this plan is available for purchase"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_subscription_type_display()})"
    
    @property
    def current_price(self):
        return self.discounted_price if self.discounted_price else self.original_price
    
    def save(self, *args, **kwargs):
        # Set default durations based on subscription type if not custom
        if self.subscription_type != 'custom' and not self.duration_in_days:
            if self.subscription_type == 'monthly':
                self.duration_in_days = 30
            elif self.subscription_type == 'quarterly':
                self.duration_in_days = 90
            elif self.subscription_type == 'yearly':
                self.duration_in_days = 365
        super().save(*args, **kwargs)

class Device(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='devices'
    )
    device_id = models.CharField(max_length=255, unique=True)
    device_name = models.CharField(max_length=100, blank=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.device_name or 'Unknown'} ({self.device_id})"

        
class PaymentTransaction(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]
    
    TRANSACTION_TYPES = [
        ('subscription', 'Subscription Purchase'),
        ('renewal', 'Subscription Renewal'),
        ('upgrade', 'Subscription Upgrade'),
        ('device', 'Device Limit Increase')
    ]
    
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='payment_transactions'
    )
    subscription_plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        default='subscription'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_gateway_reference = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='PayU')
    metadata = models.JSONField(default=dict, blank=True)  # For storing additional data like device count changes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_id} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']
        
    def mark_as_completed(self, payment_reference):
        """Mark transaction as completed and update user subscription accordingly"""
        self.status = 'completed'
        self.payment_gateway_reference = payment_reference
        self.save()
        
        if self.transaction_type == 'subscription':
            # Create or update user subscription
            start_date = timezone.now()
            end_date = start_date + timezone.timedelta(days=self.subscription_plan.duration_in_days)
            
            user_subscription, created = UserSubscription.objects.update_or_create(
                user=self.user,
                defaults={
                    'plan': self.subscription_plan,
                    'start_date': start_date,
                    'end_date': end_date,
                    'active': True
                }
            )
            return user_subscription
        
        elif self.transaction_type == 'device':
            # Upgrade device limit
            user_subscription = UserSubscription.objects.get(user=self.user)
            additional_devices = self.metadata.get('additional_devices', 1)
            user_subscription.upgrade_device_limit(additional_devices)
            return user_subscription
        
        elif self.transaction_type == 'renewal':
            # Renew existing subscription
            user_subscription = UserSubscription.objects.get(user=self.user)
            user_subscription.end_date += timezone.timedelta(days=self.subscription_plan.duration_in_days)
            user_subscription.active = True
            user_subscription.save()
            return user_subscription
        
        return None

class UserSubscription(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.SET_NULL, 
        null=True
    )
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)
    max_devices = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of devices that can access simultaneously"
    )
    devices = models.ManyToManyField(Device, blank=True)
    file_uploads_used = models.IntegerField(default=0)
    storage_used_mb = models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.user.username} - {self.plan.name if self.plan else "No Plan"}'
    
    def is_active(self):
        """Check if subscription is currently active"""
        return self.end_date > timezone.now() and self.active
    
    def can_add_device(self):
        """Check if user can add another device"""
        return self.devices.count() < self.max_devices
    
    def has_storage_space(self, file_size_mb):
        """Check if user has enough storage space for a file"""
        return (self.storage_used_mb + file_size_mb) <= (self.plan.storage_limit_mb if self.plan else 0)
    
    def can_upload_file(self):
        """Check if user can upload another file"""
        return self.file_uploads_used < (self.plan.file_upload_limit if self.plan else 0)
    
    def days_remaining(self):
        """Return number of days remaining in subscription"""
        if self.is_active():
            return (self.end_date - timezone.now()).days
        return 0
    
    def upgrade_device_limit(self, additional_devices=1):
        """Upgrade the number of allowed devices"""
        self.max_devices += additional_devices
        self.save()
    
    def add_device(self, device_id, device_name=None):
        """Add a new device to the subscription"""
        if not self.can_add_device():
            raise ValueError("Device limit reached")
        
        device, created = Device.objects.get_or_create(
            user=self.user,
            device_id=device_id,
            defaults={'device_name': device_name}
        )
        self.devices.add(device)
        return device

class InspirationPDF(models.Model):
    title = models.CharField(max_length=200)
    pdf_file = models.FileField(
        upload_to='pdfs/',
        validators=[FileExtensionValidator(['pdf'])]
    )
    preview_image = models.ImageField(
        upload_to='pdf_previews/',
        help_text="Preview image for the PDF"
    )
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def update_likes_count(self):
        self.likes_count = self.pdf_likes.count()
        self.save()

class PDFLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pdf = models.ForeignKey(
        InspirationPDF, 
        on_delete=models.CASCADE,
        related_name='pdf_likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'pdf')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.pdf.update_likes_count()

    def delete(self, *args, **kwargs):
        pdf = self.pdf
        super().delete(*args, **kwargs)
        pdf.update_likes_count()

class Palette(models.Model):
    TYPE_CHOICES = [
        ('SS', 'Spring/Summer'),
        ('AW', 'Autumn/Winter'),
        ('TR', 'Trending'),
    ]
    
    name = models.CharField(max_length=100, default="New Palette")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_palettes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    num_colors = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    base_color = models.CharField(max_length=50, default="White")
    base_color_r = models.IntegerField(
        default=255,
        validators=[MinValueValidator(0), MaxValueValidator(255)]
    )
    base_color_g = models.IntegerField(
        default=255,
        validators=[MinValueValidator(0), MaxValueValidator(255)]
    )
    base_color_b = models.IntegerField(
        default=255,
        validators=[MinValueValidator(0), MaxValueValidator(255)]
    )
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default='TR'
    )
    # Add this field to the model if you want to store the count
    favorites_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    # Rename this method to avoid conflict
    def count_favorites(self):
        return self.palette_favorites.count()

    def base_color_rgb(self):
        return f"rgb({self.base_color_r}, {self.base_color_g}, {self.base_color_b})"
    
    def update_favorites_count(self):
        """Update the cached favorites count"""
        self.favorites_count = self.palette_favorites.count()
        self.save(update_fields=['favorites_count'])

    class Meta:
        ordering = ['-created_at']
    
class Color(models.Model):
    name = models.CharField(max_length=50, blank=True)
    palette = models.ForeignKey(Palette, on_delete=models.CASCADE, related_name='colors')
    red = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)])
    green = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)])
    blue = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)])

    def __str__(self):
        return f"RGB({self.red}, {self.green}, {self.blue})"

class PaletteFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_palettes')
    palette = models.ForeignKey(Palette, on_delete=models.CASCADE, related_name='palette_favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'palette')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.palette.update_favorites_count()

    def delete(self, *args, **kwargs):
        palette = self.palette
        super().delete(*args, **kwargs)
        palette.update_favorites_count()