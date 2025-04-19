# apps/api/views.py
import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from apps.core.models import Project

# Configure logging
logger = logging.getLogger(__name__)

def home_view(request):
    return render(request, 'pages/home.html')

def about_view(request):
    return render(request, 'pages/about.html')

def plans_view(request):
    return render(request, 'pages/plans.html')

def contact_view(request):
    return render(request, 'pages/contact.html')

def privacy_policy_view(request):
    return render(request, 'pages/privacy_policy.html')

def terms_of_service_view(request):
    return render(request, 'pages/terms_of_service.html')

def affiliate_view(request):
    return render(request, 'pages/affiliate.html')

def profile_dashboard_view(request):
    logger.info(f"User {request.user.id} is attempting to view profile-dashboard")
    return render(request, 'pages/profile-dashboard.html',  {'user': request.user})

@login_required
def edit_project_view(request, user_id, project_id):
    logger.info(f"User {request.user.id} is attempting to edit project {project_id}")
    
    # Verify the requesting user matches the URL user_id
    if request.user.id != user_id:
        logger.warning(f"Permission denied: User {request.user.id} tried to access project {project_id} owned by User {user_id}")
        raise PermissionDenied("You don't have permission to edit this project")
    
    # Get the project (will return 404 if not found)
    project = get_object_or_404(Project, id=project_id, user_id=user_id)
    logger.info(f"Project {project_id} successfully retrieved for User {user_id}")
    
    # Prepare context data - using correct field names from your model
    context = {
        'user': request.user,
        'project': project,
        'original_file_url': project.original_file.url if project.original_file else None,
        'exported_image_url': project.exported_image.url if project.exported_image else None,
    }
    
    try:
        response = render(request, 'layers.html', context)
        logger.info(f"Successfully rendered layers.html for project {project_id}")
        return response
    except Exception as e:
        logger.error(f"Error rendering layers.html: {e}")
        raise