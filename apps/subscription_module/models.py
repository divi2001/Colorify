# apps\subscription_module\models.py
from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator,MinValueValidator,MaxValueValidator
from django.utils import timezone
import uuid


class PaymentTransaction(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]
    
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_transactions')
    subscription_plan = models.ForeignKey('SubscriptionPlan', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_gateway_reference = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='PayU')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_id} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']
        
    def mark_as_completed(self, payment_reference):
        """Mark transaction as completed and create/update user subscription"""
        self.status = 'completed'
        self.payment_gateway_reference = payment_reference
        self.save()
        
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
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration_in_days = models.IntegerField()

    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)

    def is_active(self):
        return self.end_date > timezone.now() and self.active

    def __str__(self):
        return f'{self.user.username} - {self.plan.name}'

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


from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

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