from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('plans/', views.plans_view, name='plans'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service_view, name='terms_of_service'),
    path('affiliate/', views.affiliate_view, name='affiliate'),
    path('profile-dashboard/', views.profile_dashboard_view, name='profile_dashboard'),
    path('edit-project/<int:user_id>/<int:project_id>/', views.edit_project_view, name='edit_project'),
    
    # Removed custom signup URL - using django-allauth's default
]