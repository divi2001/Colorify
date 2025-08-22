# apps/subscription_module/models.py
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
import uuid
import random
import string

# This model represents a subscription plan that users can purchase.
# It includes fields for the plan name, description, type, duration, pricing, limits on file uploads and storage,
# and the maximum number of devices allowed.
# It also includes methods for calculating current prices, displaying storage and device limits, and determining if a plan is popular.
# The subscription type can be monthly, quarterly, yearly, or custom.
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
        default=1024,
        help_text="Storage limit in MB"
    )
    max_devices = models.IntegerField(  # MOVED FROM UserSubscription
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of devices allowed"
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
        if self.subscription_type != 'custom' and not self.duration_in_days:
            if self.subscription_type == 'monthly':
                self.duration_in_days = 30
            elif self.subscription_type == 'quarterly':
                self.duration_in_days = 90
            elif self.subscription_type == 'yearly':
                self.duration_in_days = 365
        super().save(*args, **kwargs)
    
    def get_storage_display(self):
        """Convert storage from MB to human readable format"""
        if self.storage_limit_mb >= 2147483647:  # Max int value indicates unlimited
            return "Unlimited Storage"
        elif self.storage_limit_mb >= 1024:
            return f"{self.storage_limit_mb // 1024} GB Storage"
        else:
            return f"{self.storage_limit_mb} MB Storage"
    
    def get_file_upload_display(self):
        """Format file upload limit for display"""
        if self.file_upload_limit >= 2147483647:
            return "Unlimited File Uploads"
        else:
            return f"{self.file_upload_limit} File Uploads/month"
    
    def get_device_display(self):
        """Format device limit for display"""
        if self.max_devices >= 2147483647:
            return "Unlimited Devices"
        else:
            device_word = "Device" if self.max_devices == 1 else "Devices"
            return f"Login upto {self.max_devices} {device_word}"
    
    def get_price_display(self):
        """Get the current price to display"""
        return self.discounted_price if self.discounted_price else self.original_price
    
    def is_popular(self):
        """Determine if this plan should be marked as popular"""
        return self.name.lower() == 'pro'  # You can customize this logic

# This model represents a user's subscription, linking them to a specific plan.
# It includes fields for the user, plan, start and end dates, active status, and counts for devices, file uploads, and storage used.
# It also includes methods for checking if the subscription is active, if devices can be added, if there is enough storage space,
# and if file uploads are allowed. Additionally, it provides methods for adding and removing devices.
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
    devices = models.ManyToManyField('Device', blank=True)
    file_uploads_used = models.IntegerField(default=0)
    storage_used_mb = models.IntegerField(default=0)
    devices_used_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of devices currently being used'
    )
    
    def __str__(self):
        return f'{self.user.username} - {self.plan.name if self.plan else "No Plan"}'
    
    def is_active(self):
        """Check if subscription is currently active based on end date and active flag"""
        return self.active and self.end_date > timezone.now()
        
    def can_add_device(self):
        return self.devices_used_count < (self.plan.max_devices if self.plan else 1)
    
    def has_storage_space(self, file_size_mb):
        return (self.storage_used_mb + file_size_mb) <= (self.plan.storage_limit_mb if self.plan else 0)
    
    def can_upload_file(self):
        return self.file_uploads_used < (self.plan.file_upload_limit if self.plan else 0)
    
    def days_remaining(self):
        return (self.end_date - timezone.now()).days if self.is_active() else 0
    
    def add_device(self, device_id, device_name=None):
        if not self.can_add_device():
            raise ValueError("Device limit reached")
        
        device, created = Device.objects.get_or_create(
            user=self.user,
            device_id=device_id,
            defaults={'device_name': device_name}
        )
        if created:
            self.devices_used_count = models.F('devices_used_count') + 1
            self.save(update_fields=['devices_used_count'])
        self.devices.add(device)
        return device
    
    def remove_device(self, device_id):
        device = self.devices.filter(device_id=device_id).first()
        if device:
            self.devices.remove(device)
            self.devices_used_count = models.F('devices_used_count') - 1
            self.save(update_fields=['devices_used_count'])
            return True
        return False
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                name='unique_user_subscription'
            )
        ]
    
# This model represents a device linked to a user, allowing them to manage multiple devices under their subscription.
# It includes fields for the user, device ID, device name, last login timestamp, and active status.
# It also includes methods for saving the device and updating the last login timestamp.
# When a device is deleted, it decrements the count of devices used in the user's subscription.
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
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update last login timestamp in subscription if added
        if hasattr(self.user, 'subscription'):
            self.user.subscription.devices.add(self)
    
    def delete(self, *args, **kwargs):
        # Decrement count when device is deleted
        if hasattr(self.user, 'subscription'):
            subscription = self.user.subscription
            if self in subscription.devices.all():
                subscription.devices_used_count = models.F('devices_used_count') - 1
                subscription.save(update_fields=['devices_used_count'])
        super().delete(*args, **kwargs)


# This model is for managing referral codes that can be applied to subscription plans.
# It includes fields for the code itself, discount percentage, expiration date, usage limits, and associated plans.
# It also includes methods for checking validity, applying discounts, and generating random codes.
# It is designed to be flexible, allowing for various discount structures and plan associations.
class ReferralCode(models.Model):
    CODE_LENGTH = 8  # You can adjust this as needed
    
    code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Discount percentage (1-100)"
    )
    expiration_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Optional expiration date for the code"
    )
    max_uses = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of times this code can be used"
    )
    current_uses = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this code has been used"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this code is currently valid"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_referral_codes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    applicable_plans = models.ManyToManyField(
        SubscriptionPlan,
        blank=True,
        help_text="Plans this code applies to (leave empty for all plans)"
    )

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}% off)"
    
    @classmethod
    def generate_random_code(cls, length=CODE_LENGTH):
        """Generate a random alphanumeric code"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def is_valid(self):
        """Check if the referral code is still valid"""
        now = timezone.now()
        expired = self.expiration_date and self.expiration_date < now
        return (
            self.is_active and 
            not expired and 
            self.current_uses < self.max_uses
        )
    
    def apply_discount(self, original_price):
        """Apply the discount to a price"""
        if not self.is_valid():
            raise ValueError("Referral code is not valid")
        
        discount_amount = (original_price * self.discount_percentage) / 100
        return original_price - discount_amount
    
    def use_code(self):
        """Increment the usage count"""
        if not self.is_valid():
            raise ValueError("Referral code is not valid")
        
        self.current_uses += 1
        if self.current_uses >= self.max_uses:
            self.is_active = False
        self.save()
    
    def save(self, *args, **kwargs):
        if not self.code:
            # Generate a unique code if one isn't provided
            self.code = self.generate_random_code()
            while ReferralCode.objects.filter(code=self.code).exists():
                self.code = self.generate_random_code()
        super().save(*args, **kwargs)

# This model is for managing payment transactions related to subscriptions.
# It includes fields for the user, subscription plan, transaction type, amount, status, and payment gateway reference.
# It also includes methods for marking transactions as completed and applying referral codes if applicable.
# The transaction types can include subscription purchases, renewals, upgrades, and device limit increases.
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
        on_delete=models.CASCADE
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
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

    referral_code = models.ForeignKey(
        ReferralCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )

    # Add these new fields for Razorpay
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    
    # Update payment_method default
    payment_method = models.CharField(max_length=50, default='Razorpay')

    def __str__(self):
        return f"{self.user.username} - {self.transaction_id} - {self.status}"
    
    def mark_as_completed(self, payment_reference):
        self.status = 'completed'
        self.payment_gateway_reference = payment_reference
        self.save()
        
        # Use the referral code if applicable
        if self.referral_code and self.referral_code.is_valid():
            self.referral_code.use_code()
        
        if self.transaction_type in ['subscription', 'renewal']:
            start_date = timezone.now()
            end_date = start_date + timezone.timedelta(days=self.subscription_plan.duration_in_days)
            
            UserSubscription.objects.update_or_create(
                user=self.user,
                defaults={
                    'plan': self.subscription_plan,
                    'start_date': start_date if self.transaction_type == 'subscription' else models.F('start_date'),
                    'end_date': end_date if self.transaction_type == 'subscription' else models.F('end_date') + timezone.timedelta(days=self.subscription_plan.duration_in_days),
                    'active': True
                }
            )


# This model is for managing PDF files related to inspiration or design palettes.
# It includes fields for the title, PDF file, preview image, likes count, and timestamps for creation and updates.
# It also includes methods for updating the likes count based on user interactions.
# The PDF files can be liked by users, and the likes are counted to display popularity.
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

# This model represents a user's like on a PDF file.
# It includes fields for the user, the PDF file liked, and a timestamp for when the like was created.
# It also includes methods for saving and deleting the like, which update the likes count on the PDF.
# Each user can only like a PDF once, enforced by a unique constraint on the user and PDF fields.
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

# This model is for managing color palettes created by users.
# It includes fields for the palette name, creator, creation and update timestamps, number of colors,
# base color, type (e.g., Spring/Summer, Autumn/Winter), and a count of favorites.
# It also includes methods for counting favorites, getting the base color in RGB format, and updating the favorites count.
# The source image colors are stored as JSON to allow for flexible color management.
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
    favorites_count = models.PositiveIntegerField(default=0)
    
    # NEW FIELD - Store the original image colors as JSON
    source_image_colors = models.JSONField(null=True, blank=True, help_text="RGB colors from the original image")

    def __str__(self):
        return self.name

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

# This model represents a color within a palette.
# It includes fields for the color name, RGB values, and a foreign key to the palette it belongs to.
# It also includes methods for displaying the color in RGB format.
# The RGB values are validated to ensure they are within the range of 0-255.
class Color(models.Model):
    name = models.CharField(max_length=50, blank=True)
    palette = models.ForeignKey(Palette, on_delete=models.CASCADE, related_name='colors')
    red = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)])
    green = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)])
    blue = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(255)])

    def __str__(self):
        return f"RGB({self.red}, {self.green}, {self.blue})"

# This model represents a base color that can be used in palettes.
# It includes fields for the color name and RGB values, allowing for easy management of commonly used colors.
# The RGB values are validated to ensure they are within the range of 0-255.
# This model can be extended to include more attributes or methods as needed.    
class BaseColor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    red = models.PositiveSmallIntegerField()   # 0 to 255
    green = models.PositiveSmallIntegerField()
    blue = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.name} ({self.red}, {self.green}, {self.blue})"

# This model is for managing user favorites for palettes.
# It includes fields for the user, the palette they favorited, and a timestamp for when the favorite was created.
# It also includes methods for saving and deleting the favorite, which update the favorites count on the palette.
# Each user can only favorite a palette once, enforced by a unique constraint on the user and palette fields.
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

