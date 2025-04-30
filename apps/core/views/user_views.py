# apps\core\views\user_views.py
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import CustomUser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_name(request):
    """
    Update the user's first and last name
    """
    user = request.user
    data = request.data
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    if not first_name and not last_name:
        return Response(
            {'error': 'First name or last name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    
    user.save()
    
    return Response({
        'message': 'Name updated successfully',
        'first_name': user.first_name,
        'last_name': user.last_name
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_first_name(request):
    """
    Update the user's first name only
    """
    user = request.user
    data = request.data
    
    first_name = data.get('first_name')
    
    if not first_name:
        return Response(
            {'error': 'First name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.first_name = first_name
    user.save()
    
    return Response({
        'message': 'First name updated successfully',
        'first_name': user.first_name
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_last_name(request):
    """
    Update the user's last name only
    """
    user = request.user
    data = request.data
    
    last_name = data.get('last_name')
    
    if not last_name:
        return Response(
            {'error': 'Last name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.last_name = last_name
    user.save()
    
    return Response({
        'message': 'Last name updated successfully',
        'last_name': user.last_name
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_gender(request):
    """
    Update the user's gender
    """
    user = request.user
    data = request.data
    
    gender = data.get('gender')
    
    if not gender or gender not in ['M', 'F', 'O']:
        return Response(
            {'error': 'Valid gender is required (M, F, or O)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.gender = gender
    user.save()
    
    return Response({
        'message': 'Gender updated successfully',
        'gender': user.gender
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_designation(request):
    """
    Update the user's designation
    """
    user = request.user
    data = request.data
    
    designation = data.get('designation')
    
    if not designation:
        return Response(
            {'error': 'Designation is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.designation = designation
    user.save()
    
    return Response({
        'message': 'Designation updated successfully',
        'designation': user.designation
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change the user's password
    """
    user = request.user
    data = request.data
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        return Response(
            {'error': 'All password fields are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not user.check_password(current_password):
        return Response(
            {'error': 'Current password is incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if new_password != confirm_password:
        return Response(
            {'error': 'New passwords do not match'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.password = make_password(new_password)
    user.save()
    
    return Response({
        'message': 'Password changed successfully'
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update multiple user profile fields at once
    """
    user = request.user
    data = request.data
    
    fields_updated = []
    
    # Update name fields
    if 'first_name' in data:
        user.first_name = data['first_name']
        fields_updated.append('first_name')
    
    if 'last_name' in data:
        user.last_name = data['last_name']
        fields_updated.append('last_name')
    
    # Update gender
    if 'gender' in data and data['gender'] in ['M', 'F', 'O']:
        user.gender = data['gender']
        fields_updated.append('gender')
    
    # Update designation
    if 'designation' in data:
        user.designation = data['designation']
        fields_updated.append('designation')
    
    # Update other profile fields
    if 'phone_number' in data:
        user.phone_number = data['phone_number']
        fields_updated.append('phone_number')
    
    if 'address_line' in data:
        user.address_line = data['address_line']
        fields_updated.append('address_line')
    
    if 'city' in data:
        user.city = data['city']
        fields_updated.append('city')
    
    if 'state' in data:
        user.state = data['state']
        fields_updated.append('state')
    
    if 'country' in data:
        user.country = data['country']
        fields_updated.append('country')
    
    if not fields_updated:
        return Response(
            {'error': 'No valid fields provided for update'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.save()
    
    response_data = {
        'message': 'Profile updated successfully',
        'updated_fields': fields_updated
    }
    
    # Add updated values to response
    for field in fields_updated:
        response_data[field] = getattr(user, field)
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get the current user's profile information
    """
    user = request.user
    
    return Response({
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'gender': user.gender,
        'designation': user.designation,
        'phone_number': user.phone_number,
        'address_line': user.address_line,
        'city': user.city,
        'state': user.state,
        'country': user.country,
        'is_staff': user.is_staff,
        'date_joined': user.date_joined
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_address_line(request):
    """
    Update the user's address line
    """
    user = request.user
    data = request.data
    
    address_line = data.get('address_line')
    
    if address_line is None:
        return Response(
            {'error': 'Address line is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.address_line = address_line
    user.save()
    
    return Response({
        'message': 'Address line updated successfully',
        'address_line': user.address_line
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_city(request):
    """
    Update the user's city
    """
    user = request.user
    data = request.data
    
    city = data.get('city')
    
    if city is None:
        return Response(
            {'error': 'City is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.city = city
    user.save()
    
    return Response({
        'message': 'City updated successfully',
        'city': user.city
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_state(request):
    """
    Update the user's state
    """
    user = request.user
    data = request.data
    
    state = data.get('state')
    
    if state is None:
        return Response(
            {'error': 'State is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.state = state
    user.save()
    
    return Response({
        'message': 'State updated successfully',
        'state': user.state
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_country(request):
    """
    Update the user's country
    """
    user = request.user
    data = request.data
    
    country = data.get('country')
    
    if country is None:
        return Response(
            {'error': 'Country is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.country = country
    user.save()
    
    return Response({
        'message': 'Country updated successfully',
        'country': user.country
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_address(request):
    """
    Update all address fields at once
    """
    user = request.user
    data = request.data
    
    address_line = data.get('address_line')
    city = data.get('city')
    state = data.get('state')
    country = data.get('country')
    
    # At least one field should be provided
    if address_line is None and city is None and state is None and country is None:
        return Response(
            {'error': 'At least one address field is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if address_line is not None:
        user.address_line = address_line
    
    if city is not None:
        user.city = city
    
    if state is not None:
        user.state = state
    
    if country is not None:
        user.country = country
    
    user.save()
    
    return Response({
        'message': 'Address updated successfully',
        'address_line': user.address_line,
        'city': user.city,
        'state': user.state,
        'country': user.country
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_phone_number(request):
    """
    Update the user's phone number
    """
    user = request.user
    data = request.data
    
    phone_number = data.get('phone_number')
    
    if phone_number is None:
        return Response(
            {'error': 'Phone number is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.phone_number = phone_number
    user.save()
    
    return Response({
        'message': 'Phone number updated successfully',
        'phone_number': user.phone_number
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile_photo(request):
    try:
        user = request.user
        
        if 'profile_photo' not in request.FILES:
            return Response(
                {'error': 'No photo provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photo = request.FILES['profile_photo']
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        
        if photo.content_type not in allowed_types:
            return Response(
                {'error': 'Invalid file type. Only JPEG, PNG, and GIF are allowed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if photo.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'File size too large. Maximum size is 5 MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.profile_photo:
            user.profile_photo.delete()
        
        ext = os.path.splitext(photo.name)[1]
        filename = f"profile_{user.id}_{uuid.uuid4().hex}{ext}"
        user.profile_photo.save(filename, photo)
        user.save()
        
        return Response({
            'message': 'Profile photo updated successfully',
            'profile_photo_url': user.profile_photo.url
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile_photo(request):
    """
    Delete the user's profile photo
    """
    user = request.user
    
    if not user.profile_photo:
        return Response(
            {'error': 'No profile photo to delete'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Delete the photo file
    if os.path.isfile(user.profile_photo.path):
        os.remove(user.profile_photo.path)
    
    # Clear the field
    user.profile_photo = None
    user.save()
    
    return Response({
        'message': 'Profile photo deleted successfully'
    }, status=status.HTTP_200_OK)