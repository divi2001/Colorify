# tif_editor_project\urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from allauth.account.views import PasswordResetFromKeyView
from django.conf import settings
from django.conf.urls.static import static
from apps.mainadmin.views import admin_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('core/', include('apps.core.urls')),
    path('subscriptions/', include('apps.subscription_module.urls')),
    path('tif-editor/', include('apps.tif_to_picker.urls')),
    
    # Include allauth URLs AFTER your custom signup URL
    # This ensures your custom signup view takes precedence
    path('accounts/', include('allauth.urls')),
    path('', include('apps.api.urls')),
]

if settings.DEBUG:
    # Add the main media URL patterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Add profile photos URL patterns
    urlpatterns += static(settings.PROFILE_PHOTOS_URL, document_root=settings.PROFILE_PHOTOS_ROOT)