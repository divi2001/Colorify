# models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.db import models
import os

class Contact(models.Model):
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('support', 'Technical Support'),
        ('billing', 'Billing Question'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']

def project_file_path(instance, filename):
    # Generate a file path: projects/user_<id>/project_<id>/<filename>
    return f'projects/user_{instance.user.id}/project_{instance.id}/{filename}'

class Project(models.Model):
    STATUS_CHOICES = [
        ('drafts', 'Drafts'),
        ('exported', 'Exported'),
        ('deleted', 'Deleted'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='drafts')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    exported_at = models.DateTimeField(null=True, blank=True)
    
    # Original file (TIFF)
    original_file = models.FileField(upload_to=project_file_path, null=True, blank=True)
    
    # Exported PNG file
    exported_image = models.ImageField(upload_to=project_file_path, null=True, blank=True)
    
    # Store the original filename for reference
    original_filename = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-modified_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        base_slug = slugify(self.name)
        unique_slug = base_slug
        num = 1
        while Project.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{num}"
            num += 1
        return unique_slug

    @classmethod
    def get_next_untitled_name(cls, user):
        base_name = "Untitled Project"
        existing_projects = cls.objects.filter(user=user, name__startswith=base_name).count()
        if existing_projects == 0:
            return base_name
        return f"{base_name} {existing_projects + 1}"

    def delete_original_file(self):
        """Delete the original file if it exists"""
        if self.original_file:
            if os.path.isfile(self.original_file.path):
                os.remove(self.original_file.path)
            self.original_file = None
            self.save()

    def delete_exported_image(self):
        """Delete the exported image if it exists"""
        if self.exported_image:
            if os.path.isfile(self.exported_image.path):
                os.remove(self.exported_image.path)
            self.exported_image = None
            self.save()
    
def user_profile_photo_path(instance, filename):
    # Generate a file path: profile_photos/user_<id>/<filename>
    return f'user_{instance.id}/{filename}'

class CustomUser(AbstractUser):
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address_line = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    profile_photo = models.ImageField(upload_to=user_profile_photo_path, null=True, blank=True)

    def __str__(self):
        return self.username