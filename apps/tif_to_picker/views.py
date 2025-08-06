# apps\tif_to_picker\views.py
# Standard library imports
import os
import io
import json
import base64
import struct
import logging
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional

# Third-party imports
import cv2
import numpy as np
import tifffile
from tifffile import TiffFile, imwrite, imsave
from PIL import Image, ImageOps
from matplotlib import pyplot
import imagecodecs
from colorsys import rgb_to_hls
from psdtags import PsdChannelId
from psdtags.psdtags import TiffImageSourceData
from django.views.decorators.http import require_http_methods
# Django imports
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from apps.subscription_module.models import BaseColor
# DRF imports
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Local imports
from .forms import TiffUploadForm
from .getcolors import analyze_image_colors
from apps.core.models import Project
from apps.subscription_module.models import InspirationPDF, PDFLike, Palette
from apps.subscription_module.serializers import PaletteSerializer
from apps.subscription_module.models import SubscriptionPlan

# Logger
logger = logging.getLogger(__name__)

from .models import Mockup

import base64
import os
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings

@require_http_methods(["GET"])
def get_mockups_api(request):
    try:
        # Get all active mockups
        mockups = Mockup.objects.filter(is_active=True)
        
        mockups_data = []
        for mockup in mockups:
            mockup_data = {
                'id': mockup.id,
                'name': mockup.name,
                'description': mockup.description,
                'created_at': mockup.created_at.isoformat(),
                'image_data': None,
                'image_type': None
            }
            
            # Convert image to base64 if it exists
            if mockup.image:
                try:
                    image_path = mockup.image.path
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as image_file:
                            image_data = base64.b64encode(image_file.read()).decode('utf-8')
                            
                        # Get file extension to determine MIME type
                        file_extension = os.path.splitext(image_path)[1].lower()
                        mime_types = {
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.png': 'image/png',
                            '.gif': 'image/gif',
                            '.webp': 'image/webp'
                        }
                        
                        mockup_data['image_data'] = image_data
                        mockup_data['image_type'] = mime_types.get(file_extension, 'image/jpeg')
                except Exception as img_error:
                    print(f"Error processing image for mockup {mockup.id}: {img_error}")
            
            mockups_data.append(mockup_data)
        
        return JsonResponse({
            'success': True,
            'mockups': mockups_data,
            'count': len(mockups_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
def get_all_colors(request):
    # Fetch all color entries from the database
    colors = BaseColor.objects.all()

    # Convert the queryset to a list of dictionaries
    data = [
        {
            "name": color.name,
            "red": color.red,
            "green": color.green,
            "blue": color.blue
        }
        for color in colors
    ]

    # Return JSON response
    return JsonResponse(data, safe=False)



@api_view(['GET'])
def get_palettes(request):
    # Get query parameters
    creator_id = request.query_params.get('creator_id')
    palette_type = request.query_params.get('type')
    min_favorites = request.query_params.get('min_favorites')
    max_favorites = request.query_params.get('max_favorites')
    min_colors = request.query_params.get('min_colors')
    max_colors = request.query_params.get('max_colors')
    base_color = request.query_params.get('base_color')
    search_query = request.query_params.get('search')
    limit = request.query_params.get('limit', 10)  # Default limit is 10
    offset = request.query_params.get('offset', 0)  # Default offset is 0

    # Start with all palettes
    palettes = Palette.objects.all()

    # Apply filters based on query parameters
    if creator_id:
        palettes = palettes.filter(creator_id=creator_id)
    
    if palette_type:
        palettes = palettes.filter(type=palette_type)
    
    if min_favorites:
        palettes = palettes.filter(favorites_count__gte=min_favorites)
    
    if max_favorites:
        palettes = palettes.filter(favorites_count__lte=max_favorites)
    
    if min_colors:
        palettes = palettes.filter(num_colors__gte=min_colors)
    
    if max_colors:
        palettes = palettes.filter(num_colors__lte=max_colors)
    
    if base_color:
        palettes = palettes.filter(base_color__iexact=base_color)
    
    if search_query:
        palettes = palettes.filter(
            Q(name__icontains=search_query) | 
            Q(creator__username__icontains=search_query) |
            Q(base_color__icontains=search_query)
        )

    # Get total count before applying limit and offset
    total_count = palettes.count()

    # Apply limit and offset
    try:
        limit = int(limit)
        offset = int(offset)
    except ValueError:
        return Response({"error": "Invalid limit or offset value"}, status=status.HTTP_400_BAD_REQUEST)

    palettes = palettes[offset:offset+limit]

    # Serialize the data
    serializer = PaletteSerializer(palettes, many=True)

    return Response({
        "count": total_count,
        "results": serializer.data
    })

# Modified Django view
@api_view(['GET'])
def get_palettes_for_layers(request, total_layers):
    # Get palettes of type 'trending' with exactly total_layers colors
    palettes = Palette.objects.filter(
        type='trending',
        num_colors=total_layers
    )[:total_layers]  # Get as many as we need layers
    
    # If we don't have enough palettes, we'll need to generate more
    palettes_needed = total_layers - len(palettes)
    
    # Serialize existing palettes
    serializer = PaletteSerializer(palettes, many=True)
    palette_data = serializer.data
    
    # If we need more palettes, include a flag in response
    return Response({
        "palettes": palette_data,
        "generate_more": palettes_needed > 0,
        "palettes_needed": palettes_needed
    })


class InspirationView(View):
    def get(self, request):
        pdfs = InspirationPDF.objects.all().order_by('-created_at')
        pdfs_data = []

        for pdf in pdfs:
            liked = PDFLike.objects.filter(user=request.user, pdf=pdf).exists() if request.user.is_authenticated else False
            pdfs_data.append({
                'id': pdf.id,
                'title': pdf.title,
                'preview_image': pdf.preview_image.url if pdf.preview_image else None,
                'pdf_url': pdf.pdf_file.url if pdf.pdf_file else None,
                'likes_count': pdf.likes_count,
                'created_at': pdf.created_at.strftime('%Y-%m-%d'),
                'liked': liked
            })
        
        return JsonResponse({'pdfs': pdfs_data})

    @method_decorator(login_required)
    def post(self, request):
        pdf_id = request.POST.get('pdf_id')
        pdf = InspirationPDF.objects.get(id=pdf_id)
        like, created = PDFLike.objects.get_or_create(user=request.user, pdf=pdf)
        
        if not created:
            # User has already liked this PDF, so unlike it
            like.delete()
            liked = False
        else:
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'likes_count': pdf.likes_count
        })

inspiration_view = InspirationView.as_view()


@csrf_exempt
def analyze_color(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body)
            
            if 'imageData' not in data:
                return JsonResponse({
                    'success': False,
                    'error': 'No imageData field in request'
                })

            image_data = data['imageData']
            
            if not image_data:
                return JsonResponse({
                    'success': False,
                    'error': 'Empty image data'
                })

            # Process base64 data
            try:
                # Remove data URL prefix if present
                if isinstance(image_data, str) and 'base64,' in image_data:
                    image_data = image_data.split('base64,')[1]
                
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Error processing image data: {str(e)}'
                })

            result = analyze_image_colors(image)
            
            if result:
                return JsonResponse({
                    'success': True,
                    'colors': result
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Color analysis failed'
                })

        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid JSON: {str(e)}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    })


def process_svg_upload(request):
    if request.method == 'POST':
        try:
            tiff_file = request.FILES['tiff_file']
            file_path = os.path.join(settings.MEDIA_ROOT, tiff_file.name)
            output_dir = os.path.join(settings.MEDIA_ROOT, 'output', os.path.splitext(tiff_file.name)[0])

            # Create directories if they don't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            os.makedirs(output_dir, exist_ok=True)

            # Save uploaded file
            with open(file_path, 'wb+') as destination:
                for chunk in tiff_file.chunks():
                    destination.write(chunk)

            # Process the TIFF file
            layers = extract_layers(file_path, output_dir)
            
            # Update paths to use MEDIA_URL
            for layer in layers:
                relative_path = layer['path'].replace('\\', '/').split('media/')[-1]
                layer['path'] = settings.MEDIA_URL + relative_path

            # Get image dimensions
            with Image.open(file_path) as img:
                width, height = img.size

            # Store the layers information in session
            request.session['current_layers'] = layers
            request.session['image_width'] = width
            request.session['image_height'] = height

            return JsonResponse({
                'success': True,
                'layer_count': len(layers),
                'layers': layers,
                'width': width,
                'height': height
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # For GET requests, get layers from session if available
    layers = request.session.get('current_layers', [])
    width = request.session.get('image_width', 0)
    height = request.session.get('image_height', 0)
    
    return render(request, 'layers.html', {
        'layer_count': len(layers),
        'layers': layers,
        'width': width,
        'height': height
    })


@login_required
@login_required
def upload_tiff(request, user_id=None, project_id=None):
    """
    Handles TIFF file uploads with subscription limit enforcement
    """
    # Handle project editing case
    project = None
    if user_id and project_id:
        project = get_object_or_404(Project, id=project_id, user_id=user_id)
    
    # Initialize form
    form = TiffUploadForm(request.POST or None, request.FILES or None)
    
    # Check user subscription
    try:
        user_subscription = request.user.subscription
    except AttributeError:
        # Create default subscription if none exists
        from apps.subscription_module.models import SubscriptionPlan, UserSubscription
        try:
            default_plan = SubscriptionPlan.objects.get(name="Legacy Default Plan")
            start_date = timezone.now()
            end_date = start_date + timezone.timedelta(days=default_plan.duration_in_days)
            
            with transaction.atomic():
                user_subscription = UserSubscription.objects.create(
                    user=request.user,
                    plan=default_plan,
                    start_date=start_date,
                    end_date=end_date,
                    active=True
                )
        except Exception as e:
            logger.error(f"Failed to create default subscription: {str(e)}")
            messages.error(request, "Error initializing your account. Please contact support.")
            return redirect('home')

    if request.method == 'POST' and form.is_valid():
        tiff_file = request.FILES['tiff_file']
        
        try:
            # Calculate file size in MB (more accurate than request.FILES size)
            file_size_bytes = tiff_file.size
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            # Check subscription limits
            if not user_subscription.is_active():
                return render_limit_reached(
                    request,
                    error_message="Your subscription has expired. Please renew to continue uploading files.",
                    user_subscription=user_subscription
                )
            
            if not user_subscription.can_upload_file():
                return render_limit_reached(
                    request,
                    error_message=f"You've reached your file upload limit ({user_subscription.plan.file_upload_limit} files).",
                    user_subscription=user_subscription
                )
            
            if not user_subscription.has_storage_space(file_size_mb):
                return render_limit_reached(
                    request,
                    error_message=f"Not enough storage space. This file requires {file_size_mb:.2f}MB.",
                    user_subscription=user_subscription
                )
            
            # Create file path
            filename = f"project_{project_id}_{tiff_file.name}" if project else tiff_file.name
            file_path = os.path.join('media', 'uploads', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Generate unique temporary path
            temp_path = None
            counter = 0
            while temp_path is None or os.path.exists(temp_path):
                temp_suffix = f"_{counter}" if counter > 0 else ""
                temp_path = f"{file_path}.temp{temp_suffix}"
                counter += 1

            # Save file temporarily to get exact size
            with open(temp_path, 'wb+') as destination:
                for chunk in tiff_file.chunks():
                    destination.write(chunk)
            
            # Get precise file size after save
            precise_file_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
            
            # Final storage check with precise size
            if not user_subscription.has_storage_space(precise_file_size_mb):
                os.remove(temp_path)
                return render_limit_reached(
                    request,
                    error_message=f"File requires {precise_file_size_mb:.2f}MB (more than estimated).",
                    user_subscription=user_subscription
                )
            
            # Process the file
            output_dir = os.path.join('media', 'output', str(project_id) if project else 'demo')
            os.makedirs(output_dir, exist_ok=True)
            
            # Handle existing file
            if os.path.exists(file_path):
                try:
                    # Remove existing file
                    os.remove(file_path)
                except OSError as e:
                    logger.error(f"Error removing existing file: {e}")
                    messages.error(request, "Error updating existing file. Please try again.")
                    os.remove(temp_path)
                    return redirect(request.path)
            
            # Rename temp file to final location
            try:
                os.rename(temp_path, file_path)
            except OSError as e:
                logger.error(f"Error moving file to final location: {e}")
                os.remove(temp_path)
                messages.error(request, "Error saving file. Please try again.")
                return redirect(request.path)
            
            # Extract layers
            try:
                layers = extract_layers(file_path, output_dir)
            except Exception as e:
                logger.error(f"Error extracting layers: {e}")
                os.remove(file_path)
                messages.error(request, "Error processing TIFF layers. Please check the file format.")
                return redirect(request.path)
            
            # Convert paths for template
            for layer in layers:
                rel_path = layer['path'].replace('\\', '/').split('media/')[-1]
                layer['path'] = os.path.join(settings.MEDIA_URL, rel_path)
            
            # Update subscription metrics
            try:
                with transaction.atomic():
                    user_subscription.file_uploads_used += 1
                    user_subscription.storage_used_mb += precise_file_size_mb
                    user_subscription.save()
            except Exception as e:
                logger.error(f"Error updating subscription metrics: {e}")
                # Continue processing as this is not critical for file upload
            
            # Get image dimensions
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
            except Exception as e:
                logger.error(f"Error getting image dimensions: {e}")
                width, height = 0, 0  # Default values if dimensions can't be read
            
            # Prepare success context
            context = {
                'layer_count': len(layers),
                'layers': layers,
                'width': width,
                'height': height,
                'MEDIA_URL': settings.MEDIA_URL,
                'subscription_info': get_subscription_context(user_subscription),
                'success_message': 'File uploaded successfully!'
            }
            
            if project:
                context.update({
                    'user': request.user,
                    'project': project,
                    'is_edit_mode': True
                })
            
            return render(request, 'layers.html', context)
            
        except Exception as e:
            logger.error(f"Error processing TIFF upload: {str(e)}", exc_info=True)
            messages.error(request, f"Error processing file: {str(e)}")
            # Clean up any temporary files
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError as cleanup_error:
                    logger.error(f"Error cleaning up temporary file: {cleanup_error}")
    
    # Prepare context for GET requests or failed POST
    context = {
        'form': form,
        'subscription_info': get_subscription_context(user_subscription)
    }
    
    if project:
        context.update({
            'is_edit_mode': True,
            'project': project
        })
    
    return render(request, 'upload.html', context)

import traceback

def checkout(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    # Here you would integrate with your payment processor
    # For now, we'll just show a message
    
    messages.success(request, f"You've selected the {plan.name} plan. Payment processing would happen here.")
    return redirect('account_profile')  # Redirect to user profile or appropriate page

def render_limit_reached(request, error_message, user_subscription):
    """Helper function to render the limit reached template"""
    return render(request, 'subscription_module/limit_reached.html', {
        'error_message': error_message,
        'plan_name': user_subscription.plan.name,
        'files_used': user_subscription.file_uploads_used,
        'file_limit': user_subscription.plan.file_upload_limit,
        'files_used_percentage': (user_subscription.file_uploads_used / user_subscription.plan.file_upload_limit) * 100,
        'storage_used': user_subscription.storage_used_mb,
        'storage_limit': user_subscription.plan.storage_limit_mb,
        'storage_used_percentage': (user_subscription.storage_used_mb / user_subscription.plan.storage_limit_mb) * 100,
        'days_remaining': user_subscription.days_remaining()
    })


def get_subscription_context(user_subscription):
    """Helper function to prepare subscription context"""
    if not user_subscription or not user_subscription.plan:
        return None
    
    return {
        'plan_name': user_subscription.plan.name,
        'files_used': user_subscription.file_uploads_used,
        'file_limit': user_subscription.plan.file_upload_limit,
        'files_used_percentage': (user_subscription.file_uploads_used / user_subscription.plan.file_upload_limit) * 100,
        'storage_used': user_subscription.storage_used_mb,
        'storage_limit': user_subscription.plan.storage_limit_mb,
        'storage_used_percentage': (user_subscription.storage_used_mb / user_subscription.plan.storage_limit_mb) * 100,
        'days_remaining': user_subscription.days_remaining(),
        'is_active': user_subscription.is_active()
    }



@login_required
def upgrade_plan(request):
    available_plans = SubscriptionPlan.objects.filter(is_active=True)
    
    # Mark recommended plan (you can customize this logic)
    for plan in available_plans:
        plan.is_recommended = (plan.name == "Premium Monthly")
    
    return render(request, 'subscription_module/upgrade.html', {
        'available_plans': available_plans
    })

@csrf_exempt


def export_file(request):
    if request.method == 'POST':
        try:
            layers_data = json.loads(request.POST.get('layers_data', '[]'))
            export_format = request.POST.get('export_format', 'tiff').lower()
            
            # Validate format
            if export_format not in ['tiff', 'png', 'jpg', 'webp']:
                return JsonResponse({'error': 'Unsupported export format'}, status=400)
            
            # Create output directory
            output_dir = os.path.join('media', 'exported_files')
            os.makedirs(output_dir, exist_ok=True)
            
            processed_layers = []
            
            # Find canvas dimensions based on all layers
            max_width = 0
            max_height = 0
            
            # Collect the original physical dimensions from the metadata JSON files
            original_physical_dimensions = {}
            
            # First pass: process layers and determine canvas size
            for layer_data in layers_data:
                try:
                    base64_str = layer_data['imageData'].split(',')[1]
                    img_data = base64.b64decode(base64_str)
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Try to get the original physical dimensions from metadata
                    layer_name = layer_data['name']
                    original_width_inches = None
                    original_height_inches = None
                    
                    # Check if there's a metadata file with the original physical dimensions
                    if 'original_path' in layer_data:
                        metadata_path = os.path.splitext(layer_data['original_path'])[0] + '.metadata.json'
                        if os.path.exists(metadata_path):
                            try:
                                with open(metadata_path, 'r') as metadata_file:
                                    metadata = json.load(metadata_file)
                                    if 'physical_width_inches' in metadata and 'physical_height_inches' in metadata:
                                        original_width_inches = metadata['physical_width_inches']
                                        original_height_inches = metadata['physical_height_inches']
                                        print(f"Found original physical dimensions from metadata: {original_width_inches}\" × {original_height_inches}\"")
                            except Exception as metadata_error:
                                print(f"Error reading metadata file: {str(metadata_error)}")
                    
                    # Get DPI information from the layer data
                    dpi_x = int(layer_data.get('dpi_x', 300))
                    dpi_y = int(layer_data.get('dpi_y', 300))
                    dpi = (dpi_x, dpi_y)
                    
                    # Get physical size from the layer data or calculate from DPI
                    physical_width_inches = float(layer_data.get('physical_width_inches', img.width / dpi_x))
                    physical_height_inches = float(layer_data.get('physical_height_inches', img.height / dpi_y))
                    
                    # If we have original physical dimensions, use those instead
                    if original_width_inches is not None and original_height_inches is not None:
                        physical_width_inches = original_width_inches
                        physical_height_inches = original_height_inches
                        
                        # Recalculate DPI based on original physical dimensions
                        dpi_x = int(img.width / physical_width_inches)
                        dpi_y = int(img.height / physical_height_inches)
                        dpi = (dpi_x, dpi_y)
                    
                    # Check if we should use the original physical dimensions from the first file
                    if 'original_physical_width_inches' in layer_data and 'original_physical_height_inches' in layer_data:
                        orig_physical_width = float(layer_data['original_physical_width_inches'])
                        orig_physical_height = float(layer_data['original_physical_height_inches'])
                        
                        if orig_physical_width > 0 and orig_physical_height > 0:
                            physical_width_inches = orig_physical_width
                            physical_height_inches = orig_physical_height
                            print(f"Using original physical dimensions: {physical_width_inches}\" × {physical_height_inches}\"")
                    
                    print(f"Layer: {layer_data['name']}")
                    print(f"  Pixel dimensions: {img.width}x{img.height}")
                    print(f"  DPI: {dpi}")
                    print(f"  Physical size: {physical_width_inches:.4f}\" × {physical_height_inches:.4f}\"")
                    
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    left_pos = int(layer_data['position_left'])
                    top_pos = int(layer_data['position_top'])
                    
                    # Check if original dimensions are available
                    original_width = int(layer_data.get('original_width', 0))
                    original_height = int(layer_data.get('original_height', 0))
                    
                    # If original dimensions are specified and valid, use them
                    if original_width > 0 and original_height > 0:
                        print(f"Upscaling layer {layer_data['name']} to original dimensions: {original_width}x{original_height}")
                        
                        # Calculate scale factors
                        scale_x = original_width / img.width
                        scale_y = original_height / img.height
                        
                        # Scale position proportionally
                        left_pos = int(left_pos * scale_x)
                        top_pos = int(top_pos * scale_y)
                        
                        # Resize the image to original dimensions
                        img = img.resize((original_width, original_height), Image.LANCZOS)
                        width = original_width
                        height = original_height
                        
                        # When upscaling to original dimensions, keep the physical size the same
                        # but recalculate the DPI to maintain the physical dimensions
                        dpi_x = int(width / physical_width_inches)
                        dpi_y = int(height / physical_height_inches)
                        dpi = (dpi_x, dpi_y)
                    else:
                        # Use current dimensions
                        width = img.width
                        height = img.height
                        print(f"Using current dimensions for {layer_data['name']}: {width}x{height}")
                    
                    # Update maximum dimensions
                    max_width = max(max_width, left_pos + width)
                    max_height = max(max_height, top_pos + height)
                    
                    # Store the physical dimensions for this layer
                    original_physical_dimensions[layer_data['name']] = (physical_width_inches, physical_height_inches)
                    
                    metadata = {
                        'Name': layer_data['name'],
                        'TopPosition': top_pos,
                        'LeftPosition': left_pos,
                        'Width': width,
                        'Height': height,
                        'DPI': dpi,
                        'PhysicalWidthInches': physical_width_inches,
                        'PhysicalHeightInches': physical_height_inches,
                        'OriginalWidth': original_width if original_width > 0 else width,
                        'OriginalHeight': original_height if original_height > 0 else height
                    }
                    
                    # Store both PIL Image and numpy array
                    processed_layers.append({
                        'image': img,
                        'data': np.array(img),
                        'metadata': metadata
                    })
                    
                except Exception as e:
                    print(f"Error processing layer {layer_data.get('name', 'unknown')}: {str(e)}")
                    traceback.print_exc()
                    continue

            # Determine the physical dimensions for the entire document
            if len(original_physical_dimensions) > 0:
                # Get the maximum physical dimensions from all layers
                max_physical_width = max(dim[0] for dim in original_physical_dimensions.values())
                max_physical_height = max(dim[1] for dim in original_physical_dimensions.values())
                
                # If we have significantly larger dimensions (like our 36.5" × 58.0" example)
                # use those as the document dimensions
                if max_physical_width > 20 or max_physical_height > 20:  # Arbitrary threshold
                    document_physical_width = max_physical_width
                    document_physical_height = max_physical_height
                    print(f"Using large original dimensions: {document_physical_width}\" × {document_physical_height}\"")
                else:
                    # Calculate based on pixel dimensions and a standard DPI (like 150)
                    document_physical_width = max_width / 150
                    document_physical_height = max_height / 150
                    print(f"Using calculated dimensions: {document_physical_width}\" × {document_physical_height}\"")
            else:
                # Default calculation if we don't have original physical dimensions
                document_physical_width = max_width / 150
                document_physical_height = max_height / 150
            
            print(f"Document physical dimensions: {document_physical_width:.4f}\" × {document_physical_height:.4f}\"")
            
            # Calculate document DPI based on physical dimensions
            document_dpi_x = int(max_width / document_physical_width)
            document_dpi_y = int(max_height / document_physical_height)
            document_dpi = (document_dpi_x, document_dpi_y)
            
            print(f"Calculated document DPI: {document_dpi}")
            
            # Create a blank transparent image with the maximum dimensions
            composite_image = Image.new('RGBA', (max_width, max_height), (0, 0, 0, 0))
            
            # Paste each layer onto the composite image
            for layer in processed_layers:
                left_pos = layer['metadata']['LeftPosition']
                top_pos = layer['metadata']['TopPosition']
                composite_image.paste(
                    layer['image'],
                    (left_pos, top_pos),
                    layer['image']
                )
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Handle different export formats
            if export_format == 'tiff':
                output_path = os.path.join(output_dir, f'output_{timestamp}.tif')
                
                composite_array = np.array(composite_image)
                
                composite_metadata = {
                    'Name': 'Composite View',
                    'Width': max_width,
                    'Height': max_height,
                    'LayerCount': len(processed_layers),
                    'LayerNames': [layer['metadata']['Name'] for layer in processed_layers],
                    'IsComposite': True,
                    'DPI': document_dpi,
                    'PhysicalWidthInches': document_physical_width,
                    'PhysicalHeightInches': document_physical_height
                }
                
                # Write multi-page TIFF with high quality settings
                with tifffile.TiffWriter(output_path) as tif:
                    # Write composite as first page with the document DPI
                    tif.write(
                        composite_array,
                        photometric='rgb',
                        planarconfig='contig',
                        metadata=composite_metadata,
                        compression='adobe_deflate',
                        compressionargs={'level': 9},
                        resolutionunit='INCH',
                        resolution=document_dpi,
                        description='Composite View'
                    )
                    
                    # Write individual layers with consistent DPI values
                    for layer in processed_layers:
                        layer_full = np.zeros((max_height, max_width, 4), dtype=np.uint8)
                        h, w = layer['data'].shape[:2]
                        top = layer['metadata']['TopPosition']
                        left = layer['metadata']['LeftPosition']
                        layer_full[top:top+h, left:left+w] = layer['data']
                        
                        # Update the layer metadata to use the document DPI
                        layer['metadata']['DPI'] = document_dpi
                        
                        # Use the document DPI for all layers to ensure consistency
                        tif.write(
                            layer_full,
                            photometric='rgb',
                            planarconfig='contig',
                            metadata=layer['metadata'],
                            compression='adobe_deflate',
                            compressionargs={'level': 9},
                            resolutionunit='INCH',
                            resolution=document_dpi,
                            description=layer['metadata']['Name']
                        )
                
                content_type = 'image/tiff'
                
            else:
                # For other formats (PNG, JPG, WebP), export composite only
                file_extensions = {
                    'png': 'png',
                    'jpg': 'jpg', 
                    'webp': 'webp'
                }
                
                output_path = os.path.join(output_dir, f'output_{timestamp}.{file_extensions[export_format]}')
                
                # Convert to appropriate mode for different formats
                if export_format == 'jpg':
                    # JPG doesn't support transparency, convert to RGB with white background
                    background = Image.new('RGB', composite_image.size, (255, 255, 255))
                    background.paste(composite_image, mask=composite_image.split()[-1])  # Use alpha channel as mask
                    composite_image = background
                    save_kwargs = {'quality': 95, 'optimize': True}
                elif export_format == 'png':
                    save_kwargs = {'optimize': True}
                elif export_format == 'webp':
                    save_kwargs = {'quality': 95, 'method': 6}  # method=6 for best compression
                
                # Save with DPI information
                composite_image.save(output_path, dpi=document_dpi, **save_kwargs)
                
                content_types = {
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'webp': 'image/webp'
                }
                content_type = content_types[export_format]

            # Read the file and send it as a response
            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="exported_{timestamp}.{file_extensions.get(export_format, "tif")}"'
                return response

        except Exception as e:
            error_msg = f"Export error: {str(e)}"
            traceback.print_exc()  # Print full traceback for debugging
            print(error_msg)
            return JsonResponse({'error': error_msg}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_layer_image(layer):
    try:
        channels_data = []
        for channel in layer.channels:
            if channel.channelid in [PsdChannelId.CHANNEL0, PsdChannelId.CHANNEL1, PsdChannelId.CHANNEL2]:
                if channel.data.ndim == 2:
                    channels_data.append(channel.data)
                else:
                    print(
                        f"Unexpected channel data shape: {channel.data.shape}")

        if len(channels_data) == 3:
            image_data = np.stack(channels_data, axis=-1)
            return image_data
        else:
            print(f"Unexpected number of channels: {len(channels_data)}")
            return None
    except Exception as e:
        print(f"Error retrieving layer image: {str(e)}")
        return None


def cmyk_to_rgb(c, m, y, k):
    r = 255 * (1 - c / 100) * (1 - k / 100)
    g = 255 * (1 - m / 100) * (1 - k / 100)
    b = 255 * (1 - y / 100) * (1 - k / 100)
    return [r / 255, g / 255, b / 255]

def lab_to_rgb(l, a, b):
    y = (l + 16) / 116
    x = a / 500 + y
    z = y - b / 200

    x = 0.95047 * (x * x * x if x * x * x > 0.008856 else (x - 16/116) / 7.787)
    y = 1.00000 * (y * y * y if y * y * y > 0.008856 else (y - 16/116) / 7.787)
    z = 1.08883 * (z * z * z if z * z * z > 0.008856 else (z - 16/116) / 7.787)

    r = x *  3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y *  1.8758 + z *  0.0415
    b = x *  0.0557 + y * -0.2040 + z *  1.0570

    r = 1 if r > 1 else 0 if r < 0 else r
    g = 1 if g > 1 else 0 if g < 0 else g
    b = 1 if b > 1 else 0 if b < 0 else b

    return [r, g, b]

def parse_color_data(layer):
    """Parse color data from Color Fill layer."""
    try:
        # First check if it's a Color Fill layer
        if not any(hasattr(item, 'key') and item.key == PsdKey.SOLID_COLOR_SHEET_SETTING 
                  for item in layer.info):
            return None

        # Get the solid color data
        for item in layer.info:
            if getattr(item, 'key', None) == PsdKey.SOLID_COLOR_SHEET_SETTING:
                color_data = item.value
                
                # Color mode identifier is stored in the data
                if len(color_data) >= 16:
                    color_mode = struct.unpack('>I', color_data[12:16])[0]
                    
                    # Debug print
                    print(f"Color mode: {color_mode}")
                    print(f"Color data hex: {color_data.hex()}")
                    
                    # Extract color values based on mode
                    if len(color_data) >= 46:
                        if color_mode == 0:  # RGB
                            r, g, b = struct.unpack('>HHH', color_data[40:46])
                            return [x / 65535.0 for x in (r, g, b)]
                        
                        elif color_mode == 2:  # CMYK
                            if len(color_data) >= 48:
                                c, m, y, k = struct.unpack('>HHHH', color_data[40:48])
                                c, m, y, k = [x / 65535.0 for x in (c, m, y, k)]
                                r = (1 - c) * (1 - k)
                                g = (1 - m) * (1 - k)
                                b = (1 - y) * (1 - k)
                                return [r, g, b]
                        
                        elif color_mode == 7:  # Lab
                            l, a, b = struct.unpack('>HHH', color_data[40:46])
                            l = (l / 65535.0) * 100
                            a = ((a / 65535.0) * 255) - 128
                            b = ((b / 65535.0) * 255) - 128
                            
                            # Convert Lab to RGB (simplified conversion)
                            y = (l + 16) / 116
                            x = a / 500 + y
                            z = y - b / 200
                            
                            x = 0.95047 * (x * x * x if x * x * x > 0.008856 else (x - 16/116) / 7.787)
                            y = 1.00000 * (y * y * y if y * y * y > 0.008856 else (y - 16/116) / 7.787)
                            z = 1.08883 * (z * z * z if z * z * z > 0.008856 else (z - 16/116) / 7.787)
                            
                            r = x *  3.2406 + y * -1.5372 + z * -0.4986
                            g = x * -0.9689 + y *  1.8758 + z *  0.0415
                            b = x *  0.0557 + y * -0.2040 + z *  1.0570
                            
                            return [max(0, min(1, c)) for c in (r, g, b)]
                
                # If we couldn't parse the color data in a known format, try to find any color information
                print("Attempting to parse alternative color formats...")
                for i in range(0, len(color_data)-6, 2):
                    try:
                        values = struct.unpack('>HHH', color_data[i:i+6])
                        if all(0 <= v <= 65535 for v in values):
                            print(f"Found potential color values at offset {i}: {values}")
                            return [v / 65535.0 for v in values]
                    except:
                        continue
                
    except Exception as e:
        print(f"Error parsing color data: {str(e)}")
    return None

def is_color_fill_layer(layer):
    """Check if the layer is a Color Fill layer."""
    if not hasattr(layer, 'info'):
        return False
    return any(hasattr(item, 'key') and item.key == PsdKey.SOLID_COLOR_SHEET_SETTING 
              for item in layer.info)
def extract_layers(file_path, output_dir, output_format='PNG', quality=100, max_dimension=4000, optimize=True):
    """
    Extract and compress layers from image files.
    
    Parameters:
    file_path (str): Path to input image file (TIFF, JPEG, PNG)
    output_dir (str): Directory to save extracted layers
    output_format (str): Output format ('PNG', 'JPEG', 'WEBP')
    quality (int): Compression quality (1-100) for JPEG/WEBP
    max_dimension (int): Maximum dimension for width/height (maintains aspect ratio)
    optimize (bool): Apply additional optimization
    """
    import tifffile
    from PIL import Image, ExifTags
    import os
    import numpy as np
    from matplotlib import pyplot
    import piexif
    from PIL.Image import Resampling
    import json
    import struct
    from fractions import Fraction

    # Increase PIL's maximum image size limit
    Image.MAX_IMAGE_PIXELS = None  # Disable the decompression bomb warning
    
    def get_dpi_and_physical_size(file_path):
        """Extract both DPI and physical dimensions (in inches) from an image file"""
        default_dpi = (300, 300)
        physical_size_inches = None
        dpi = default_dpi
        
        try:
            # For TIFF files, use tifffile to get accurate measurements
            if file_path.lower().endswith(('.tif', '.tiff')):
                with tifffile.TiffFile(file_path) as tif:
                    if len(tif.pages) > 0:
                        page = tif.pages[0]
                        
                        # Get pixel dimensions
                        pixel_width = page.imagewidth
                        pixel_height = page.imagelength
                        
                        # Extract resolution information
                        if 'XResolution' in page.tags and 'YResolution' in page.tags:
                            x_resolution = page.tags['XResolution'].value
                            y_resolution = page.tags['YResolution'].value
                            
                            # Handle rational numbers
                            if isinstance(x_resolution, tuple) and len(x_resolution) == 2:
                                x_dpi = x_resolution[0] / x_resolution[1]
                            else:
                                x_dpi = x_resolution
                                
                            if isinstance(y_resolution, tuple) and len(y_resolution) == 2:
                                y_dpi = y_resolution[0] / y_resolution[1]
                            else:
                                y_dpi = y_resolution
                            
                            # Check resolution unit (1 = none, 2 = inch, 3 = cm)
                            resolution_unit = page.tags.get('ResolutionUnit', 2).value
                            if resolution_unit == 3:  # Convert from cm to inches
                                x_dpi = x_dpi * 2.54
                                y_dpi = y_dpi * 2.54
                            
                            dpi = (int(x_dpi), int(y_dpi))
                            
                            # Calculate physical size in inches
                            physical_width_inches = pixel_width / x_dpi
                            physical_height_inches = pixel_height / y_dpi
                            physical_size_inches = (physical_width_inches, physical_height_inches)
                            
                            print(f"TIFF physical size: {physical_width_inches:.4f}\" × {physical_height_inches:.4f}\" at {dpi} DPI")
                            return dpi, physical_size_inches
            
            # For other formats, use PIL
            with Image.open(file_path) as img:
                # Get pixel dimensions
                pixel_width, pixel_height = img.size
                
                # Try to get DPI from PIL
                if 'dpi' in img.info:
                    dpi = img.info['dpi']
                    x_dpi, y_dpi = dpi
                    
                    # Calculate physical size in inches
                    physical_width_inches = pixel_width / x_dpi
                    physical_height_inches = pixel_height / y_dpi
                    physical_size_inches = (physical_width_inches, physical_height_inches)
                    
                    print(f"PIL physical size: {physical_width_inches:.4f}\" × {physical_height_inches:.4f}\" at {dpi} DPI")
                    return dpi, physical_size_inches
                
                # For JPEGs, try EXIF data
                if file_path.lower().endswith(('.jpg', '.jpeg')):
                    try:
                        exif = img._getexif()
                        if exif:
                            x_dpi = None
                            y_dpi = None
                            resolution_unit = 2  # Default to inches
                            
                            # Look for resolution tags in EXIF
                            for tag_id, value in exif.items():
                                tag_name = ExifTags.TAGS.get(tag_id, '')
                                if tag_name == 'XResolution':
                                    x_dpi = value[0] / value[1] if isinstance(value, tuple) else value
                                elif tag_name == 'YResolution':
                                    y_dpi = value[0] / value[1] if isinstance(value, tuple) else value
                                elif tag_name == 'ResolutionUnit':
                                    resolution_unit = value
                            
                            if x_dpi and y_dpi:
                                # If resolution unit is in cm, convert to inches
                                if resolution_unit == 3:
                                    x_dpi = x_dpi * 2.54
                                    y_dpi = y_dpi * 2.54
                                
                                dpi = (int(x_dpi), int(y_dpi))
                                
                                # Calculate physical size in inches
                                physical_width_inches = pixel_width / x_dpi
                                physical_height_inches = pixel_height / y_dpi
                                physical_size_inches = (physical_width_inches, physical_height_inches)
                                
                                print(f"EXIF physical size: {physical_width_inches:.4f}\" × {physical_height_inches:.4f}\" at {dpi} DPI")
                                return dpi, physical_size_inches
                    except:
                        pass
            
            # If we couldn't determine physical size, use default DPI
            physical_width_inches = pixel_width / default_dpi[0]
            physical_height_inches = pixel_height / default_dpi[1]
            physical_size_inches = (physical_width_inches, physical_height_inches)
            
            print(f"Default physical size: {physical_width_inches:.4f}\" × {physical_height_inches:.4f}\" at {default_dpi} DPI")
            return default_dpi, physical_size_inches
            
        except Exception as e:
            print(f"Error measuring physical size: {str(e)}")
            return default_dpi, None
    
    def get_dpi_from_tiff_page(page):
        """Extract DPI and physical dimensions from a TIFF page"""
        default_dpi = (300, 300)
        physical_size_inches = None
        
        try:
            # Get pixel dimensions
            pixel_width = page.imagewidth
            pixel_height = page.imagelength
            
            # Get resolution tags
            if 'XResolution' in page.tags and 'YResolution' in page.tags:
                x_resolution = page.tags['XResolution'].value
                y_resolution = page.tags['YResolution'].value
                
                # Resolution values are often stored as rational numbers (tuples)
                if isinstance(x_resolution, tuple) and len(x_resolution) == 2:
                    x_dpi = x_resolution[0] / x_resolution[1]
                else:
                    x_dpi = x_resolution
                    
                if isinstance(y_resolution, tuple) and len(y_resolution) == 2:
                    y_dpi = y_resolution[0] / y_resolution[1]
                else:
                    y_dpi = y_resolution
                
                # Check resolution unit (1 = none, 2 = inch, 3 = cm)
                resolution_unit = page.tags.get('ResolutionUnit', 2).value
                if resolution_unit == 3:  # Convert from cm to inches if needed
                    x_dpi = x_dpi * 2.54
                    y_dpi = y_dpi * 2.54
                
                dpi = (int(x_dpi), int(y_dpi))
                
                # Calculate physical size in inches
                physical_width_inches = pixel_width / x_dpi
                physical_height_inches = pixel_height / y_dpi
                physical_size_inches = (physical_width_inches, physical_height_inches)
                
                print(f"TIFF page physical size: {physical_width_inches:.4f}\" × {physical_height_inches:.4f}\" at {dpi} DPI")
                return dpi, physical_size_inches
            else:
                print(f"No resolution tags found, using default {default_dpi} DPI")
                
                # Calculate physical size using default DPI
                physical_width_inches = pixel_width / default_dpi[0]
                physical_height_inches = pixel_height / default_dpi[1]
                physical_size_inches = (physical_width_inches, physical_height_inches)
                
                return default_dpi, physical_size_inches
                
        except Exception as e:
            print(f"Error getting physical size from TIFF page: {str(e)}")
            return default_dpi, None
    
    def compress_and_save_image(image_array, output_path, original_size=None, dpi=(300, 300), physical_size_inches=None):
        try:
            # Convert numpy array to PIL Image
            if isinstance(image_array, np.ndarray):
                # Handle different array types and shapes
                if image_array.dtype == np.float32 or image_array.dtype == np.float64:
                    image_array = (image_array * 255).astype(np.uint8)
                elif image_array.dtype == bool:  # Handle binary masks
                    image_array = image_array.astype(np.uint8) * 255
                
                # Ensure proper shape for PIL
                if len(image_array.shape) == 2:  # Grayscale
                    img = Image.fromarray(image_array, 'L')
                elif len(image_array.shape) == 3:  # RGB/RGBA
                    if image_array.shape[2] == 3:
                        img = Image.fromarray(image_array, 'RGB')
                    elif image_array.shape[2] == 4:
                        img = Image.fromarray(image_array, 'RGBA')
                    else:
                        raise ValueError(f"Unexpected array shape: {image_array.shape}")
            else:
                img = image_array

            # Get original dimensions - store these before any resize happens
            orig_width, orig_height = img.size
            
            # If we didn't get physical size, calculate it from DPI
            if physical_size_inches is None:
                physical_width_inches = orig_width / dpi[0]
                physical_height_inches = orig_height / dpi[1]
                physical_size_inches = (physical_width_inches, physical_height_inches)
            else:
                physical_width_inches, physical_height_inches = physical_size_inches
            
            print(f"Original dimensions: {orig_width}x{orig_height}, "
                  f"Physical size: {physical_width_inches:.4f}\" × {physical_height_inches:.4f}\" at {dpi} DPI")
            
            # Store original dimensions to return
            original_dimensions = (orig_width, orig_height)
            
            # Set ML label to 1 (hardcoded)
            ml_label = 1

            # Resize if max_dimension is specified and image exceeds it
            resized = False
            if max_dimension and (orig_width > max_dimension or orig_height > max_dimension):
                if orig_width > orig_height:
                    new_width = max_dimension
                    new_height = int((orig_height * max_dimension) / orig_width)
                else:
                    new_height = max_dimension
                    new_width = int((orig_width * max_dimension) / orig_height)
                
                print(f"Resizing to: {new_width}x{new_height}")
                img = img.resize((new_width, new_height), Resampling.LANCZOS)
                resized = True
                
                # When we resize, we need to recalculate DPI to maintain physical size
                if physical_size_inches:
                    new_x_dpi = new_width / physical_width_inches
                    new_y_dpi = new_height / physical_height_inches
                    dpi = (int(new_x_dpi), int(new_y_dpi))
                    print(f"Adjusted DPI after resize: {dpi}")

            # Convert color mode if necessary
            if output_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                # Convert to RGB, removing transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                else:
                    background.paste(img)
                img = background
            elif img.mode not in ('RGB', 'RGBA', 'L'):
                img = img.convert('RGB')

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Save with format-specific optimizations
            try:
                if output_format.upper() == 'PNG':
                    # For PNG, we need to set up the pHYs chunk for DPI
                    ppm_x = int(dpi[0] / 0.0254)  # Convert DPI to pixels per meter
                    ppm_y = int(dpi[1] / 0.0254)
                    
                    # Create a new PNG info object
                    png_info = None
                    try:
                        from PIL import PngImagePlugin
                        png_info = PngImagePlugin.PngInfo()
                        png_info.add_text("Software", "Python PIL")
                        
                        # Add physical pixel dimensions
                        # This adds the pHYs chunk with pixels per meter and unit = 1 (meters)
                        png_info.add(b'pHYs', struct.pack('>IIB', ppm_x, ppm_y, 1))
                    except:
                        print("Warning: Could not create PNG info")
                    
                    # Save the PNG with DPI information
                    img.save(output_path, 
                           'PNG',
                           optimize=optimize,
                           compress_level=9,
                           dpi=dpi,
                           pnginfo=png_info)
                    
                    # Double check with a more reliable method for critical files
                    try:
                        import png
                        # Read the written file
                        with open(output_path, 'rb') as f:
                            reader = png.Reader(file=f)
                            w, h, pixels, metadata = reader.read()
                        
                        # Create a new file with explicitly set physical information
                        with open(output_path, 'wb') as f:
                            writer = png.Writer(
                                width=w,
                                height=h,
                                alpha='alpha' in metadata,
                                bitdepth=metadata.get('bitdepth', 8),
                                compression=9,
                                physical=(ppm_x, ppm_y, 1)  # This sets the pHYs chunk
                            )
                            writer.write(f, pixels)
                    except Exception as png_err:
                        print(f"Warning: pypng rewrite failed: {str(png_err)}")
                
                elif output_format.upper() == 'JPEG':
                    # JPEG DPI handling
                    # Convert DPI to rational numbers for EXIF
                    def dpi_to_rational(dpi_value):
                        fraction = Fraction(dpi_value).limit_denominator(65535)
                        return (fraction.numerator, fraction.denominator)
                    
                    x_dpi_rational = dpi_to_rational(dpi[0])
                    y_dpi_rational = dpi_to_rational(dpi[1])
                    
                    # Basic save with PIL's DPI parameter
                    img.save(output_path, 
                           'JPEG',
                           quality=quality,
                           optimize=optimize,
                           progressive=True,
                           dpi=dpi)
                    
                    # Add more explicit EXIF resolution data
                    try:
                        # Create EXIF dictionary
                        exif_dict = {"0th": {}, "Exif": {}, "1st": {}, "GPS": {}}
                        
                        # Add resolution data to EXIF
                        exif_dict["0th"][piexif.ImageIFD.XResolution] = x_dpi_rational
                        exif_dict["0th"][piexif.ImageIFD.YResolution] = y_dpi_rational
                        exif_dict["0th"][piexif.ImageIFD.ResolutionUnit] = 2  # inches
                        
                        # Convert to bytes and insert into image
                        exif_bytes = piexif.dump(exif_dict)
                        piexif.insert(exif_bytes, output_path)
                    except Exception as exif_err:
                        print(f"Warning: Could not add EXIF resolution: {str(exif_err)}")
                
                elif output_format.upper() == 'WEBP':
                    # WebP doesn't directly support DPI in PIL
                    img.save(output_path, 
                           'WEBP',
                           quality=quality,
                           method=6,  # Highest compression method
                           lossless=False)
                    
                    # For WebP, we rely completely on the metadata file
                else:
                    raise ValueError(f"Unsupported output format: {output_format}")

                # Print compression stats if original size is provided
                if original_size:
                    new_size = os.path.getsize(output_path)
                    reduction = ((original_size - new_size) / original_size) * 100
                    print(f"Size reduced by {reduction:.1f}% ({original_size/1024/1024:.1f}MB -> {new_size/1024/1024:.1f}MB)")

                # Save metadata about dimensions and physical size to a companion file
                metadata_path = os.path.splitext(output_path)[0] + '.metadata.json'
                metadata = {
                    'original_width': orig_width,
                    'original_height': orig_height,
                    'display_width': img.width,
                    'display_height': img.height,
                    'dpi_x': dpi[0],
                    'dpi_y': dpi[1],
                    'physical_width_inches': physical_width_inches,
                    'physical_height_inches': physical_height_inches,
                    'ml_label': ml_label
                }
                
                with open(metadata_path, 'w') as metadata_file:
                    json.dump(metadata, metadata_file)

                return img.size, original_dimensions, ml_label, dpi, physical_size_inches

            except Exception as save_error:
                print(f"Error saving image: {str(save_error)}")
                if os.path.exists(output_path):
                    os.remove(output_path)  # Clean up partial file
                return None, None, None, None, None

        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None, None, None, None, None

    # Check file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension in ['.jpg', '.jpeg', '.png']:
        # Handle JPEG/PNG files
        try:
            original_size = os.path.getsize(file_path)
            
            # Get both DPI and physical size from the file
            dpi, physical_size_inches = get_dpi_and_physical_size(file_path)
            print(f"Using DPI {dpi} and physical size {physical_size_inches} for {file_path}")
            
            with Image.open(file_path) as img:
                full_image = np.array(img)
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            base_filename = os.path.splitext(os.path.basename(file_path))[0]
            layer_output_path = os.path.join(output_dir, f"{base_filename}.{output_format.lower()}")
            
            # Pass the physical size to maintain exact dimensions
            size, orig_size, ml_label, dpi, physical_size = compress_and_save_image(
                full_image, layer_output_path, original_size, dpi=dpi, physical_size_inches=physical_size_inches
            )
            
            if size is None:
                return []
            
            width, height = size
            orig_width, orig_height = orig_size
            physical_width_inches, physical_height_inches = physical_size
            
            return [{
                'name': base_filename,
                'path': layer_output_path,
                'layer_position_from_top': 0,
                'layer_position_from_left': 0,
                'width': width,
                'height': height,
                'original_width': orig_width,
                'original_height': orig_height,
                'dpi_x': dpi[0],
                'dpi_y': dpi[1],
                'physical_width_inches': physical_width_inches,
                'physical_height_inches': physical_height_inches,
                'ml_label': ml_label
            }]
            
        except Exception as e:
            print(f"Error processing {file_extension} file: {str(e)}")
            return []
        
    elif file_extension in ['.tiff', '.tif']:
        try:
            # Read TIFF file
            with tifffile.TiffFile(file_path) as tif:
                # Get the number of pages/layers
                n_pages = len(tif.pages)
                original_size = os.path.getsize(file_path) // max(1, n_pages)  # Approximate size per layer
                
                print(f"Processing TIFF file with {n_pages} pages")
                
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                layers_info = []
                
                # Process each page as a layer
                for i, page in enumerate(tif.pages, 1):
                    try:
                        # Get the image data
                        image = page.asarray()
                        
                        # Extract both DPI and physical dimensions
                        dpi, physical_size_inches = get_dpi_from_tiff_page(page)
                        print(f"Layer {i} - DPI: {dpi}, Physical size: {physical_size_inches}")
                        
                        # Create layer name
                        layer_name = f"layer_{i}"
                        
                        # Try to get a better name from metadata if available
                        try:
                            if hasattr(page, 'description') and page.description:
                                better_name = page.description.strip()
                                if better_name:  # Use description as name if available
                                    layer_name = better_name
                                    print(f"Using description as layer name: {layer_name}")
                        except:
                            pass
                        
                        # Create output path
                        layer_output_path = os.path.join(output_dir, f"{layer_name}.{output_format.lower()}")
                        
                        print(f"Processing layer {i}/{n_pages}: {layer_name}")
                        
                        # Pass both DPI and physical dimensions to maintain exact sizing
                        size, orig_size, ml_label, dpi, physical_size = compress_and_save_image(
                            image, layer_output_path, original_size, dpi=dpi, physical_size_inches=physical_size_inches
                        )
                        
                        if size is None:
                            continue
                        
                        width, height = size
                        orig_width, orig_height = orig_size
                        physical_width_inches, physical_height_inches = physical_size
                        
                        # Add layer info
                        layer_info = {
                            'name': layer_name,
                            'path': layer_output_path,
                            'layer_position_from_top': 0,
                            'layer_position_from_left': 0,
                            'width': width,
                            'height': height,
                            'original_width': orig_width,
                            'original_height': orig_height,
                            'dpi_x': dpi[0],
                            'dpi_y': dpi[1],
                            'physical_width_inches': physical_width_inches,
                            'physical_height_inches': physical_height_inches,
                            'ml_label': ml_label
                        }
                        
                        layers_info.append(layer_info)
                        
                    except Exception as e:
                        print(f"Error processing layer {i}: {str(e)}")
                        continue
                
                return layers_info
                
        except Exception as e:
            print(f"Error processing TIFF file: {str(e)}")
            return []
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")
    
def extractColors():
    print("testing")

def extractColors():
    print("testing")

def single_layer_color_picker(request):
    tiff_file = request.FILES['tiff_file']
    # print(tiff_file)
    file_path = os.path.join('media', tiff_file.name)
    # print(file_path)
    with open(file_path, 'wb+') as destination:
        for chunk in tiff_file.chunks():
            destination.write(chunk)

    # Process the TIFF file

    layers = extract_layers(file_path, 'media/output/'+tiff_file.name)

    return render(request, 'single_layers.html', {'layers': layers})
    # return render(request, "layer_color_picker.html")