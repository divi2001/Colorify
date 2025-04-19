"""
URL configuration for tif_editor_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# tif_editor_project\urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from allauth.account.views import PasswordResetFromKeyView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('core/', include('apps.core.urls')),
    path('subscription/', include('apps.subscription_module.urls')),
    path('tif-editor/', include('apps.tif_to_picker.urls')),
    # path('mainadmin', include('apps.mainadmin.urls')),

    # The main password reset URL
    # re_path(
    #     r"^accounts/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
    #     PasswordResetFromKeyView.as_view(template_name="account/password_reset_from_key.html"),
    #     name="account_reset_password_from_key"
    # ),
    # The done view
    path('accounts/', include('allauth.urls')),
    path('', include('apps.api.urls')),
]

if settings.DEBUG:
    # Add the main media URL patterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Add profile photos URL patterns
    urlpatterns += static(settings.PROFILE_PHOTOS_URL, document_root=settings.PROFILE_PHOTOS_ROOT)