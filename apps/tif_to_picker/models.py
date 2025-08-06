# In your models.py
from django.db import models
from django.conf import settings
import base64
import os

class Mockup(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='mockups/', blank=True, null=True)  # Keep this for admin uploads
    image_base64 = models.TextField(blank=True, null=True)  # Store base64 data
    image_type = models.CharField(max_length=20, default='image/png')  # Store MIME type
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # If image is uploaded but no base64 data, convert it
        if self.image and not self.image_base64:
            try:
                # Read the image file
                image_path = self.image.path
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as image_file:
                        image_data = base64.b64encode(image_file.read()).decode('utf-8')
                        self.image_base64 = image_data
                        
                        # Determine MIME type from file extension
                        file_extension = os.path.splitext(image_path)[1].lower()
                        mime_types = {
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.png': 'image/png',
                            '.gif': 'image/gif',
                            '.webp': 'image/webp'
                        }
                        self.image_type = mime_types.get(file_extension, 'image/png')
            except Exception as e:
                print(f"Error converting image to base64: {e}")
        
        super().save(*args, **kwargs)
    
    def get_image_data_url(self):
        """Return the complete data URL for use in img src"""
        if self.image_base64:
            return f"data:{self.image_type};base64,{self.image_base64}"
        return None
    
    def __str__(self):
        return self.name