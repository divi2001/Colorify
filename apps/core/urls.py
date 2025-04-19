# urls.py
from django.urls import path
from .views.project_views import (
    contact_form_submission,
    create_new_project,
    project_list,
    rename_project,
    delete_project
)
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
    update_profile_photo,
    delete_profile_photo
)

urlpatterns = [
    # Project endpoints
    path('contact-form-submission/', contact_form_submission, name='contact-form-submission'),
    path('create-new-project/', create_new_project, name='create-new-project'),
    path('projects/', project_list, name='project-list'),
    path('projects/<int:project_id>/rename/', rename_project, name='rename-project'),
    path('projects/<int:project_id>/delete/', delete_project, name='delete-project'),
    
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
    
    # User photo endpoints
    path('users/update-profile-photo/', update_profile_photo, name='update-profile-photo'),
    path('users/delete-profile-photo/', delete_profile_photo, name='delete-profile-photo'),
]