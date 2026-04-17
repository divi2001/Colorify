# apps\core\urls.py
from django.urls import path
from .views.project_views import (
    create_new_project,
    project_list,
    rename_project,
    delete_project
)
from .views.contact_views import (
    contact_form_submission,
    affiliate_form_submission,
    reset_sessions_and_continue_login,
)
from .views.newsletter_views import newsletter_subscribe, newsletter_unsubscribe
from .views.user_views import (
    update_user_name,
    update_first_name,
    update_last_name,
    update_gender,
    update_designation,
    change_password,
    update_profile,
    get_user_profile,
    update_address_line,
    update_city,
    update_state,
    update_country,
    update_address,
    update_phone_number,
    update_company_details,
    update_profile_photo,
    delete_profile_photo,
    check_username_availability,
    check_email_availability
)

urlpatterns = [
    # Contact and Affiliate endpoints
    path('contact-form-submission/', contact_form_submission, name='contact-form-submission'),
    path('affiliate-form-submission/', affiliate_form_submission, name='affiliate-form-submission'),
    path('reset-sessions-and-login/', reset_sessions_and_continue_login, name='reset-sessions-and-login'),
    path('newsletter-subscribe/', newsletter_subscribe, name='newsletter-subscribe'),
    path('newsletter-unsubscribe/<str:token>/', newsletter_unsubscribe, name='newsletter-unsubscribe'),
    
    # Project endpoints
    path('create-new-project/', create_new_project, name='create-new-project'),
    path('projects/', project_list, name='project-list'),
    path('projects/<int:project_id>/rename/', rename_project, name='rename-project'),
    path('projects/<int:project_id>/delete/', delete_project, name='delete-project'),
    
    # User validation endpoints (public)
    path('check-username/', check_username_availability, name='check-username-availability'),
    path('check-email/', check_email_availability, name='check-email-availability'),
    
    # User profile endpoints
    path('users/update-name/', update_user_name, name='update-user-name'),
    path('users/update-first-name/', update_first_name, name='update-first-name'),
    path('users/update-last-name/', update_last_name, name='update-last-name'),
    path('users/update-gender/', update_gender, name='update-gender'),
    path('users/update-designation/', update_designation, name='update-designation'),
    path('users/change-password/', change_password, name='change-password'),
    path('users/update-profile/', update_profile, name='update-profile'),
    path('users/profile/', get_user_profile, name='get-user-profile'),
    
    # User address endpoints
    path('users/update-address-line/', update_address_line, name='update-address-line'),
    path('users/update-city/', update_city, name='update-city'),
    path('users/update-state/', update_state, name='update-state'),
    path('users/update-country/', update_country, name='update-country'),
    path('users/update-address/', update_address, name='update-address'),
    path('users/update-phone-number/', update_phone_number, name='update-phone-number'),
    path('users/update-company-details/', update_company_details, name='update-company-details'),
    
    # User photo endpoints
    path('users/update-profile-photo/', update_profile_photo, name='update-profile-photo'),
    path('users/delete-profile-photo/', delete_profile_photo, name='delete-profile-photo'),
]