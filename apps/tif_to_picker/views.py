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
from django.utils import timezone
from datetime import datetime
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
                'has_image': bool(mockup.image_base64),
                'image_data_url': mockup.get_image_data_url()  # Complete data URL ready for img src
            }
            mockups_data.append(mockup_data)
        
        return JsonResponse({
            'success': True,
            'mockups': mockups_data,
            'count': len(mockups_data)
        })
        
    except Exception as e:
        print(f"Error in get_mockups_api: {e}")
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


def download_pdf(request, pdf_id):
    """Download or view PDF file"""
    print(f"🔍 download_pdf called with pdf_id: {pdf_id}")
    print(f"📡 Request method: {request.method}")
    print(f"🌐 Request path: {request.path}")
    
    try:
        print(f"🔎 Looking for PDF with ID: {pdf_id}")
        pdf = get_object_or_404(InspirationPDF, id=pdf_id)
        print(f"✅ Found PDF: {pdf.title}")
        
        # Check if the PDF file exists
        if not pdf.pdf_file or not pdf.pdf_file.name:
            print(f"❌ PDF {pdf_id} has no file attached")
            logger.error(f"PDF {pdf_id} has no file attached")
            return HttpResponse("PDF file not found", status=404)
        
        print(f"📁 PDF file path: {pdf.pdf_file.name}")
        print(f"💾 Full file path: {pdf.pdf_file.path}")
        
        # Check if the file exists on disk
        if not os.path.exists(pdf.pdf_file.path):
            print(f"❌ PDF file does not exist on disk: {pdf.pdf_file.path}")
            logger.error(f"PDF file does not exist on disk: {pdf.pdf_file.path}")
            return HttpResponse("PDF file not found on disk", status=404)
        
        print(f"✅ PDF file exists on disk")
        
        # Open and serve the PDF file
        with open(pdf.pdf_file.path, 'rb') as pdf_file:
            print(f"📖 Reading PDF file...")
            file_content = pdf_file.read()
            print(f"📊 PDF file size: {len(file_content)} bytes")
            
            response = HttpResponse(file_content, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{pdf.title}.pdf"'
            print(f"🚀 Returning PDF response with content-type: application/pdf")
            return response
        
    except InspirationPDF.DoesNotExist:
        print(f"❌ PDF with ID {pdf_id} does not exist")
        logger.error(f"PDF with ID {pdf_id} does not exist")
        return HttpResponse("PDF not found", status=404)
    except Exception as e:
        print(f"💥 Error serving PDF {pdf_id}: {str(e)}")
        logger.error(f"Error serving PDF {pdf_id}: {str(e)}")
        return HttpResponse(f"Error serving PDF: {str(e)}", status=500)


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


# Initialize recolorer globally (like Flask version)
_recolorer = None
_processing_lock = None
_lock_timestamp = None

def get_recolorer():
    """Get or create the global recolorer instance."""
    global _recolorer
    if _recolorer is None:
        from .palette_recolor_standalone import PaletteRecolor
        _recolorer = PaletteRecolor(sample_level=16, luminance_flag=True)
    return _recolorer

def get_processing_lock():
    """Get or create the global processing lock."""
    global _processing_lock, _lock_timestamp
    if _processing_lock is None:
        import threading
        _processing_lock = threading.Lock()
        _lock_timestamp = None
    
    # Check if lock is stuck (held for more than 60 seconds)
    if _lock_timestamp is not None:
        import time
        if time.time() - _lock_timestamp > 60:
            print("⚠️ Lock was stuck for >60s, force releasing...")
            try:
                _processing_lock.release()
            except:
                pass
            _lock_timestamp = None
    
    return _processing_lock

def update_lock_timestamp():
    """Update the timestamp when lock is acquired."""
    global _lock_timestamp
    import time
    _lock_timestamp = time.time()

def clear_lock_timestamp():
    """Clear the timestamp when lock is released."""
    global _lock_timestamp
    _lock_timestamp = None


def decode_image_data(image_data):
    """
    Decode image data from various formats.
    Supports: base64 data URL, raw base64, or file upload
    """
    try:
        # If it's a data URL (data:image/png;base64,...)
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            # Extract base64 part
            base64_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(base64_data)
        elif isinstance(image_data, str):
            # Try as raw base64
            image_bytes = base64.b64decode(image_data)
        else:
            # Assume it's already bytes
            image_bytes = image_data
        
        # Open as PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    except Exception as e:
        raise ValueError(f"Failed to decode image: {str(e)}")


@csrf_exempt
def process_image_with_jimp(request):
    """
    Django endpoint for palette-based image recoloring.
    Compatible with existing frontend that sends colorMappings.
    
    Expected request:
    - Form data with 'image' file OR 'imageData' base64
    - 'colorMappings' JSON string with format:
      [
        {"originalColor": [r, g, b], "targetColor": [r, g, b]},
        ...
      ]
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed'
        }, status=405)
    
    # Get the processing lock
    lock = get_processing_lock()
    
    # Try to acquire lock without blocking
    acquired = lock.acquire(blocking=False)
    
    if not acquired:
        # Another request is being processed
        return JsonResponse({
            'success': False,
            'error': 'Server is busy processing another image. Please wait and try again.',
            'busy': True
        }, status=503)
    
    # Mark when lock was acquired
    update_lock_timestamp()
    
    try:
        print("=" * 60)
        print("Received image processing request")
        
        # Get recolorer instance
        recolorer = get_recolorer()
        
        # Get image data
        image = None
        
        # Try to get from file upload first
        if 'image' in request.FILES:
            print("Loading image from file upload")
            file = request.FILES['image']
            # Read file content and use decode_image_data for consistency
            file_content = file.read()
            image = Image.open(io.BytesIO(file_content))
            if image.mode != 'RGB':
                image = image.convert('RGB')
        
        # Try to get from form data
        elif 'imageData' in request.POST:
            print("Loading image from imageData")
            image_data = request.POST['imageData']
            image = decode_image_data(image_data)
        
        # Try to get from JSON body
        elif request.content_type == 'application/json':
            print("Loading image from JSON body")
            data = json.loads(request.body)
            if 'imageData' in data:
                image = decode_image_data(data['imageData'])
            elif 'image' in data:
                image = decode_image_data(data['image'])
        
        if image is None:
            return JsonResponse({
                'success': False,
                'error': 'No image data provided. Send as "image" file or "imageData" base64'
            }, status=400)
        
        print(f"Image loaded: {image.size}")
        
        # Get color mappings
        color_mappings_str = None
        if 'colorMappings' in request.POST:
            color_mappings_str = request.POST['colorMappings']
        elif request.content_type == 'application/json':
            data = json.loads(request.body)
            if 'colorMappings' in data:
                color_mappings_str = json.dumps(data['colorMappings'])
        
        if not color_mappings_str:
            return JsonResponse({
                'success': False,
                'error': 'No colorMappings provided'
            }, status=400)
        
        # Parse color mappings
        color_mappings = json.loads(color_mappings_str)
        print(f"Color mappings: {len(color_mappings)} pairs")
        
        # Extract original and target colors
        original_colors = []
        target_colors = []
        
        for mapping in color_mappings:
            original = mapping.get('originalColor')
            target = mapping.get('targetColor')
            
            if original and target:
                # Ensure they're tuples of 3 integers
                original_colors.append(tuple([int(c) for c in original[:3]]))
                target_colors.append(tuple([int(c) for c in target[:3]]))
        
        if not original_colors or not target_colors:
            return JsonResponse({
                'success': False,
                'error': 'Invalid color mappings format'
            }, status=400)
        
        print(f"Original colors: {original_colors}")
        print(f"Target colors: {target_colors}")
        
        # Save image temporarily (same as Flask version - simple temp file)
        temp_input = 'temp_input.png'
        image.save(temp_input)
        
        # Apply palette-based recoloring
        print("Applying palette-based recoloring...")
        result_image = recolorer.recolor_image(
            image_path=temp_input,
            original_colors=original_colors,
            new_colors=target_colors,
            output_path=None  # Return PIL Image
        )
        
        # Clean up temp file
        if os.path.exists(temp_input):
            os.remove(temp_input)
        
        # Encode result to base64
        print("Encoding result...")
        buffer = io.BytesIO()
        result_image.save(buffer, format='PNG')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        result_base64 = f'data:image/png;base64,{image_base64}'
        
        print("Processing complete!")
        print("=" * 60)
        
        return JsonResponse({
            'success': True,
            'processedImage': result_base64,
            'message': 'Image processed successfully'
        })
    
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
    finally:
        # Always release the lock when done
        try:
            lock.release()
            clear_lock_timestamp()
            print("✅ Released processing lock")
        except Exception as e:
            print(f"⚠️ Error releasing lock: {e}")


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
    logger.info(f"User {request.user.id} accessed upload_tiff view")
    
    # Handle project editing case
    project = None
    if user_id and project_id:
        project = get_object_or_404(Project, id=project_id, user_id=user_id)
    
    # Initialize form
    form = TiffUploadForm(request.POST or None, request.FILES or None)
    
    # Check user subscription
    try:
        user_subscription = request.user.subscription
        print(f"🔍 DEBUG: Found existing subscription for user {request.user.id}")
    except AttributeError:
        print(f"🔍 DEBUG: No subscription found, creating default for user {request.user.id}")
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
                print(f"Created/renewed subscription for user {request.user.id} with plan {default_plan.name}")
        except Exception as e:
            logger.error(f"Failed to create default subscription: {str(e)}")
            messages.error(request, "Error initializing your account. Please contact support.")
            return redirect('home')

    # Add comprehensive subscription debugging
    print(f"🔍 DEBUG: === SUBSCRIPTION STATUS ===")
    print(f"  User: {request.user.id}")
    print(f"  Plan: {user_subscription.plan.name}")
    print(f"  Start Date: {user_subscription.start_date}")
    print(f"  End Date: {user_subscription.end_date}")
    print(f"  Active (DB field): {getattr(user_subscription, 'active', 'NO ACTIVE FIELD')}")
    print(f"  Files Used: {user_subscription.file_uploads_used}")
    print(f"  File Limit: {user_subscription.plan.file_upload_limit}")
    print(f"  Storage Used (MB): {user_subscription.storage_used_mb}")
    print(f"  Storage Limit (MB): {user_subscription.plan.storage_limit_mb}")
    print(f"🔍 DEBUG: ============================")

    if request.method == 'POST' and form.is_valid():
        tiff_file = request.FILES['tiff_file']
        
        try:
            print(f"🔍 DEBUG: Processing file: {tiff_file.name}")
            print(f"🔍 DEBUG: File size: {tiff_file.size} bytes")
            
            # Calculate file size in MB (more accurate than request.FILES size)
            file_size_bytes = tiff_file.size
            file_size_mb = file_size_bytes / (1024 * 1024)
            print(f"🔍 DEBUG: File size in MB: {file_size_mb:.2f}")
            
            # DETAILED SUBSCRIPTION LIMIT CHECKS WITH DEBUG
            print(f"🔍 DEBUG: === CHECKING SUBSCRIPTION LIMITS ===")
            
            # Check 1: Subscription Active
            is_active_result = user_subscription.is_active()
            print(f"🔍 DEBUG: is_active() method returned: {is_active_result}")
            if not is_active_result:
                print(f"🚨 LIMIT HIT: Subscription not active")
                return render_limit_reached(
                    request,
                    error_message="Your subscription has expired. Please renew to continue uploading files.",
                    user_subscription=user_subscription
                )
            
            # Check 2: File Upload Limit
            can_upload_result = user_subscription.can_upload_file()
            print(f"🔍 DEBUG: can_upload_file() method returned: {can_upload_result}")
            print(f"🔍 DEBUG: Files check: {user_subscription.file_uploads_used} < {user_subscription.plan.file_upload_limit} = {user_subscription.file_uploads_used < user_subscription.plan.file_upload_limit}")
            if not can_upload_result:
                print(f"🚨 LIMIT HIT: Cannot upload file - file limit reached")
                return render_limit_reached(
                    request,
                    error_message=f"You've reached your file upload limit ({user_subscription.plan.file_upload_limit} files).",
                    user_subscription=user_subscription
                )
            
            # Check 3: Storage Space
            has_storage_result = user_subscription.has_storage_space(file_size_mb)
            print(f"🔍 DEBUG: has_storage_space({file_size_mb:.2f}) method returned: {has_storage_result}")
            print(f"🔍 DEBUG: Storage check: {user_subscription.storage_used_mb} + {file_size_mb:.2f} <= {user_subscription.plan.storage_limit_mb} = {(user_subscription.storage_used_mb + file_size_mb) <= user_subscription.plan.storage_limit_mb}")
            if not has_storage_result:
                print(f"🚨 LIMIT HIT: Not enough storage space")
                return render_limit_reached(
                    request,
                    error_message=f"Not enough storage space. This file requires {file_size_mb:.2f}MB.",
                    user_subscription=user_subscription
                )
            
            print(f"🔍 DEBUG: ✅ All subscription checks passed - proceeding with upload")
            print(f"🔍 DEBUG: ==========================================")
            
            # Create file path
            filename = f"project_{project_id}_{tiff_file.name}" if project else tiff_file.name
            file_path = os.path.join('media', 'uploads', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            print(f"🔍 DEBUG: File will be saved to: {file_path}")
            
            # Generate unique temporary path
            temp_path = None
            counter = 0
            while temp_path is None or os.path.exists(temp_path):
                temp_suffix = f"_{counter}" if counter > 0 else ""
                temp_path = f"{file_path}.temp{temp_suffix}"
                counter += 1

            print(f"🔍 DEBUG: Using temporary path: {temp_path}")

            # Save file temporarily to get exact size
            with open(temp_path, 'wb+') as destination:
                for chunk in tiff_file.chunks():
                    destination.write(chunk)
            
            print(f"🔍 DEBUG: File saved temporarily")
            
            # Get precise file size after save
            precise_file_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
            print(f"🔍 DEBUG: Precise file size: {precise_file_size_mb:.2f}MB")
            
            # Final storage check with precise size
            has_precise_storage = user_subscription.has_storage_space(precise_file_size_mb)
            print(f"🔍 DEBUG: Final storage check with precise size: {has_precise_storage}")
            if not has_precise_storage:
                print(f"🚨 LIMIT HIT: File requires more space than estimated")
                os.remove(temp_path)
                return render_limit_reached(
                    request,
                    error_message=f"File requires {precise_file_size_mb:.2f}MB (more than estimated).",
                    user_subscription=user_subscription
                )
            
            # Process the file
            output_dir = os.path.join('media', 'output', str(project_id) if project else 'demo')
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"🔍 DEBUG: Output directory: {output_dir}")
            
            # Handle existing file
            if os.path.exists(file_path):
                try:
                    # Remove existing file
                    os.remove(file_path)
                    print(f"🔍 DEBUG: Removed existing file: {file_path}")
                except OSError as e:
                    logger.error(f"Error removing existing file: {e}")
                    messages.error(request, "Error updating existing file. Please try again.")
                    os.remove(temp_path)
                    return redirect(request.path)
            
            # Rename temp file to final location
            try:
                os.rename(temp_path, file_path)
                print(f"🔍 DEBUG: File moved to final location: {file_path}")
            except OSError as e:
                logger.error(f"Error moving file to final location: {e}")
                os.remove(temp_path)
                messages.error(request, "Error saving file. Please try again.")
                return redirect(request.path)
            
            # Extract layers
            try:
                print(f"🔍 DEBUG: Starting layer extraction...")
                layers = extract_layers(file_path, output_dir)
                print(f"🔍 DEBUG: Extracted {len(layers)} layers")
                
                for i, layer in enumerate(layers):
                    print(f"🔍 DEBUG: Layer {i+1}: {layer}")
                    
            except Exception as e:
                logger.error(f"Error extracting layers: {e}")
                print(f"🔍 DEBUG: Layer extraction failed: {e}")
                os.remove(file_path)
                messages.error(request, "Error processing TIFF layers. Please check the file format.")
                return redirect(request.path)
            
            # Convert paths for template
            print(f"🔍 DEBUG: Converting paths for template...")
            print(f"🔍 DEBUG: MEDIA_URL: {settings.MEDIA_URL}")
            
            for i, layer in enumerate(layers):
                original_path = layer['path']
                rel_path = layer['path'].replace('\\', '/').split('media/')[-1]
                layer['path'] = os.path.join(settings.MEDIA_URL, rel_path).replace('\\', '/')
                print(f"🔍 DEBUG: Layer {i+1} path: {original_path} -> {layer['path']}")
            
            # Update subscription metrics
            try:
                print(f"🔍 DEBUG: Updating subscription metrics...")
                print(f"🔍 DEBUG: Before update - Files: {user_subscription.file_uploads_used}, Storage: {user_subscription.storage_used_mb}MB")
                
                with transaction.atomic():
                    user_subscription.file_uploads_used += 1
                    user_subscription.storage_used_mb += precise_file_size_mb
                    user_subscription.save()
                    
                print(f"🔍 DEBUG: After update - Files: {user_subscription.file_uploads_used}, Storage: {user_subscription.storage_used_mb}MB")
                
            except Exception as e:
                logger.error(f"Error updating subscription metrics: {e}")
                # Continue processing as this is not critical for file upload
            
            # Get image dimensions
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                print(f"🔍 DEBUG: Image dimensions: {width}x{height}")
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
            
            print(f"🔍 DEBUG: Template context prepared:")
            print(f"    - layer_count: {context['layer_count']}")
            print(f"    - layers: {len(context['layers'])} items")
            print(f"    - MEDIA_URL: {context['MEDIA_URL']}")
            print(f"🔍 DEBUG: ✅ SUCCESS - Rendering layers.html template")
            
            if project:
                context.update({
                    'user': request.user,
                    'project': project,
                    'is_edit_mode': True
                })
                print(f"🔍 DEBUG: Added project context for project {project.id}")
            
            return render(request, 'layers.html', context)
            
        except Exception as e:
            logger.error(f"Error processing TIFF upload: {str(e)}", exc_info=True)
            print(f"🔍 DEBUG: ❌ Exception in upload processing: {str(e)}")
            messages.error(request, f"Error processing file: {str(e)}")
            # Clean up any temporary files
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError as cleanup_error:
                    logger.error(f"Error cleaning up temporary file: {cleanup_error}")
    else:
        print(f"🔍 DEBUG: GET request or form invalid")
        if request.method == 'POST':
            print(f"🔍 DEBUG: Form errors: {form.errors}")
    
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
    
    print(f"🔍 DEBUG: Rendering upload template (GET request or failed POST)")
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
    today = timezone.now().date()
    end_date = user_subscription.end_date
    if isinstance(end_date, datetime):  # normalize if datetime
        end_date = end_date.date()

    days_remaining = max((end_date - today).days, 0)
    is_active_calc = end_date >= today

    print("=== DEBUG: render_limit_reached ===")
    print("Plan:", user_subscription.plan.name)
    print("End Date (normalized):", end_date)
    print("Today:", today)
    print("Days Remaining:", days_remaining)
    print("Active field (DB):", getattr(user_subscription, "active", None))
    print("is_active (calculated):", is_active_calc)
    print("====================================")
    print("=== DEBUG: upload_tiff limits check ===")
    print("Files used:", user_subscription.file_uploads_used)
    print("File limit:", user_subscription.plan.file_upload_limit)
    print("Storage used (MB):", user_subscription.storage_used_mb)
    print("Storage limit (MB):", user_subscription.plan.storage_limit_mb)


    return render(request, 'subscription_module/limit_reached.html', {
        'error_message': error_message,
        'plan_name': user_subscription.plan.name,
        'files_used': user_subscription.file_uploads_used,
        'file_limit': user_subscription.plan.file_upload_limit,
        'files_used_percentage': (user_subscription.file_uploads_used / user_subscription.plan.file_upload_limit) * 100,
        'storage_used': user_subscription.storage_used_mb,
        'storage_limit': user_subscription.plan.storage_limit_mb,
        'storage_used_percentage': (user_subscription.storage_used_mb / user_subscription.plan.storage_limit_mb) * 100,
        'days_remaining': days_remaining
    })


def get_subscription_context(user_subscription):
    if not user_subscription or not user_subscription.plan:
        print("=== DEBUG: No active subscription or plan ===")
        return None

    today = timezone.now().date()
    end_date = user_subscription.end_date
    if isinstance(end_date, datetime):  # if it's a datetime, normalize
        end_date = end_date.date()

    days_remaining = max((end_date - today).days, 0)
    is_active_calc = end_date >= today

    print("=== DEBUG: get_subscription_context ===")
    print("Plan:", user_subscription.plan.name)
    print("End Date (normalized):", end_date)
    print("Today:", today)
    print("Days Remaining:", days_remaining)
    print("Active field (DB):", getattr(user_subscription, "active", None))
    print("is_active (calculated):", is_active_calc)
    print("========================================")

    return {
        'plan_name': user_subscription.plan.name,
        'files_used': user_subscription.file_uploads_used,
        'file_limit': user_subscription.plan.file_upload_limit,
        'files_used_percentage': (user_subscription.file_uploads_used / user_subscription.plan.file_upload_limit) * 100,
        'storage_used': user_subscription.storage_used_mb,
        'storage_limit': user_subscription.plan.storage_limit_mb,
        'storage_used_percentage': (user_subscription.storage_used_mb / user_subscription.plan.storage_limit_mb) * 100,
        'days_remaining': days_remaining,
        'is_active': is_active_calc
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
            use_original_resolution = request.POST.get('use_original_resolution') == 'true'
            
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
            
            print(f"Processing {len(layers_data)} layers for export (use_original: {use_original_resolution})")
            
            # Process layers - prioritize processed canvas data if available
            for layer_data in layers_data:
                try:
                    img = None
                    layer_name = layer_data.get('name', 'unknown')
                    palette_applied = layer_data.get('palette_applied', False)
                    
                    print(f"Processing layer {layer_name}, palette_applied: {palette_applied}")
                    
                    # IMPORTANT CHANGE: Check if we have processed canvas data first
                    # This takes priority over original files when transformations have been applied
                    if 'current_canvas_data' in layer_data and layer_data['current_canvas_data']:
                        print(f"Using processed canvas data for {layer_name} (palette applied: {palette_applied})")
                        
                        # Use the processed canvas data (with palette transformations)
                        base64_str = layer_data['current_canvas_data'].split(',')[1]
                        img_data = base64.b64decode(base64_str)
                        img = Image.open(io.BytesIO(img_data))
                        
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        
                        # The processed image should already be at the correct resolution
                        # Get scaled positions (these should already be scaled in the frontend)
                        left_pos = int(layer_data.get('position_left', 0))
                        top_pos = int(layer_data.get('position_top', 0))
                        
                        print(f"Loaded processed image: {img.width}x{img.height}")
                        
                    # Fallback: Try to use original high-resolution image if no processed data
                    elif use_original_resolution and 'original_path' in layer_data and layer_data['original_path']:
                        original_path = layer_data['original_path']
                        print(f"Loading original image for {layer_name}: {original_path}")
                        
                        if os.path.exists(original_path):
                            try:
                                img = Image.open(original_path)
                                if img.mode != 'RGBA':
                                    img = img.convert('RGBA')
                                print(f"Loaded original image: {img.width}x{img.height}")
                                
                                # Get scaled positions (these should already be scaled in the frontend)
                                left_pos = int(layer_data.get('position_left', 0))
                                top_pos = int(layer_data.get('position_top', 0))
                                
                            except Exception as img_error:
                                print(f"Error loading original image {original_path}: {str(img_error)}")
                                img = None
                        else:
                            print(f"Original image not found: {original_path}")
                    
                    # Final fallback to display canvas data
                    if img is None:
                        print(f"Using display canvas data fallback for {layer_name}")
                        
                        # Use imageData as final fallback
                        image_data_key = 'imageData' if 'imageData' in layer_data else None
                        if image_data_key:
                            base64_str = layer_data[image_data_key].split(',')[1]
                            img_data = base64.b64decode(base64_str)
                            img = Image.open(io.BytesIO(img_data))
                            
                            if img.mode != 'RGBA':
                                img = img.convert('RGBA')
                            
                            # Use original positions without scaling
                            left_pos = int(layer_data.get('position_left', 0))
                            top_pos = int(layer_data.get('position_top', 0))
                            
                            # If we have original dimensions and we're using original resolution,
                            # scale up the display canvas
                            if use_original_resolution:
                                original_width = int(layer_data.get('original_width', 0))
                                original_height = int(layer_data.get('original_height', 0))
                                
                                if original_width > 0 and original_height > 0:
                                    print(f"Scaling up display canvas to original size: {original_width}x{original_height}")
                                    
                                    # Calculate scale factors
                                    scale_x = original_width / img.width
                                    scale_y = original_height / img.height
                                    
                                    # Scale the image
                                    img = img.resize((original_width, original_height), Image.LANCZOS)
                                    
                                    # Scale positions
                                    left_pos = int(left_pos * scale_x)
                                    top_pos = int(top_pos * scale_y)
                        else:
                            print(f"No image data found for layer {layer_name}")
                            continue
                    
                    # Get physical dimensions and DPI
                    dpi_x = int(layer_data.get('dpi_x', 300))
                    dpi_y = int(layer_data.get('dpi_y', 300))
                    dpi = (dpi_x, dpi_y)
                    
                    # Get physical size
                    physical_width_inches = float(layer_data.get('physical_width_inches', img.width / dpi_x))
                    physical_height_inches = float(layer_data.get('physical_height_inches', img.height / dpi_y))
                    
                    # Try to get original physical dimensions
                    if 'original_physical_width_inches' in layer_data and 'original_physical_height_inches' in layer_data:
                        orig_physical_width = float(layer_data['original_physical_width_inches'])
                        orig_physical_height = float(layer_data['original_physical_height_inches'])
                        
                        if orig_physical_width > 0 and orig_physical_height > 0:
                            physical_width_inches = orig_physical_width
                            physical_height_inches = orig_physical_height
                            
                            # Recalculate DPI based on current image size and original physical dimensions
                            dpi_x = int(img.width / physical_width_inches)
                            dpi_y = int(img.height / physical_height_inches)
                            dpi = (dpi_x, dpi_y)
                            print(f"Using original physical dimensions: {physical_width_inches:.4f}\" × {physical_height_inches:.4f}\"")
                    
                    # Also check metadata file for physical dimensions
                    metadata_path = None
                    if 'original_path' in layer_data and layer_data['original_path']:
                        metadata_path = os.path.splitext(layer_data['original_path'])[0] + '.metadata.json'
                    
                    if metadata_path and os.path.exists(metadata_path):
                        try:
                            with open(metadata_path, 'r') as metadata_file:
                                metadata = json.load(metadata_file)
                                if 'physical_width_inches' in metadata and 'physical_height_inches' in metadata:
                                    physical_width_inches = metadata['physical_width_inches']
                                    physical_height_inches = metadata['physical_height_inches']
                                    
                                    # Recalculate DPI
                                    dpi_x = int(img.width / physical_width_inches)
                                    dpi_y = int(img.height / physical_height_inches)
                                    dpi = (dpi_x, dpi_y)
                                    print(f"Found physical dimensions in metadata: {physical_width_inches:.4f}\" × {physical_height_inches:.4f}\"")
                        except Exception as metadata_error:
                            print(f"Error reading metadata file: {str(metadata_error)}")
                    
                    print(f"Layer: {layer_name}")
                    print(f"  Final dimensions: {img.width}x{img.height}")
                    print(f"  Position: ({left_pos}, {top_pos})")
                    print(f"  DPI: {dpi}")
                    print(f"  Physical size: {physical_width_inches:.4f}\" × {physical_height_inches:.4f}\"")
                    print(f"  Palette applied: {palette_applied}")
                    
                    # Update maximum dimensions
                    max_width = max(max_width, left_pos + img.width)
                    max_height = max(max_height, top_pos + img.height)
                    
                    metadata = {
                        'Name': layer_name,
                        'TopPosition': top_pos,
                        'LeftPosition': left_pos,
                        'Width': img.width,
                        'Height': img.height,
                        'DPI': dpi,
                        'PhysicalWidthInches': physical_width_inches,
                        'PhysicalHeightInches': physical_height_inches,
                        'OriginalWidth': int(layer_data.get('original_width', img.width)),
                        'OriginalHeight': int(layer_data.get('original_height', img.height)),
                        'UseOriginalResolution': use_original_resolution,
                        'PaletteApplied': palette_applied
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

            if not processed_layers:
                return JsonResponse({'error': 'No layers could be processed'}, status=400)

            # Determine document physical dimensions
            if processed_layers:
                # Get maximum physical dimensions from all layers
                max_physical_width = max(layer['metadata']['PhysicalWidthInches'] for layer in processed_layers)
                max_physical_height = max(layer['metadata']['PhysicalHeightInches'] for layer in processed_layers)
                
                # Use the larger physical dimensions for the document
                document_physical_width = max_physical_width
                document_physical_height = max_physical_height
            else:
                # Fallback calculation
                document_physical_width = max_width / 300
                document_physical_height = max_height / 300
            
            # Calculate document DPI
            document_dpi_x = int(max_width / document_physical_width) if document_physical_width > 0 else 300
            document_dpi_y = int(max_height / document_physical_height) if document_physical_height > 0 else 300
            document_dpi = (document_dpi_x, document_dpi_y)
            
            print(f"Final document:")
            print(f"  Pixel dimensions: {max_width}x{max_height}")
            print(f"  Physical dimensions: {document_physical_width:.4f}\" × {document_physical_height:.4f}\"")
            print(f"  Document DPI: {document_dpi}")
            
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
            resolution_suffix = "_highres" if use_original_resolution else "_display"
            
            # Handle different export formats
            if export_format == 'tiff':
                output_path = os.path.join(output_dir, f'output{resolution_suffix}_{timestamp}.tif')
                
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
                    'PhysicalHeightInches': document_physical_height,
                    'UseOriginalResolution': use_original_resolution,
                    'PaletteApplied': any(layer['metadata'].get('PaletteApplied', False) for layer in processed_layers)
                }
                
                # Write multi-page TIFF with high quality settings
                with tifffile.TiffWriter(output_path) as tif:
                    # Write composite as first page
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
                    
                    # Write individual layers
                    for layer in processed_layers:
                        layer_full = np.zeros((max_height, max_width, 4), dtype=np.uint8)
                        h, w = layer['data'].shape[:2]
                        top = layer['metadata']['TopPosition']
                        left = layer['metadata']['LeftPosition']
                        layer_full[top:top+h, left:left+w] = layer['data']
                        
                        # Update layer metadata with document DPI
                        layer['metadata']['DPI'] = document_dpi
                        
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
                
                output_path = os.path.join(output_dir, f'output{resolution_suffix}_{timestamp}.{file_extensions[export_format]}')
                
                # Convert to appropriate mode for different formats
                if export_format == 'jpg':
                    # JPG doesn't support transparency
                    background = Image.new('RGB', composite_image.size, (255, 255, 255))
                    background.paste(composite_image, mask=composite_image.split()[-1])
                    composite_image = background
                    save_kwargs = {'quality': 95, 'optimize': True}
                elif export_format == 'png':
                    save_kwargs = {'optimize': True}
                elif export_format == 'webp':
                    save_kwargs = {'quality': 95, 'method': 6}
                
                # Save with DPI information
                composite_image.save(output_path, dpi=document_dpi, **save_kwargs)
                
                content_types = {
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'webp': 'image/webp'
                }
                content_type = content_types[export_format]

            # Read the file and send it as a response
            file_extension = file_extensions.get(export_format, 'tif')
            filename = f'exported{resolution_suffix}_{timestamp}.{file_extension}'
            
            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

        except Exception as e:
            error_msg = f"Export error: {str(e)}"
            traceback.print_exc()
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
import os
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    from torchvision import models
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
from PIL import Image

# Original Lightweight CNN Model (for backward compatibility)
if TORCH_AVAILABLE:
    class LightweightCNN(nn.Module):
        def __init__(self, num_classes=2):
            super(LightweightCNN, self).__init__()
            self.features = nn.Sequential(
                nn.Conv2d(3, 32, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.BatchNorm2d(32),
                nn.Conv2d(32, 64, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.BatchNorm2d(64),
                nn.Conv2d(64, 128, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.BatchNorm2d(128),
                nn.Conv2d(128, 64, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.BatchNorm2d(64),
                nn.AdaptiveAvgPool2d((1, 1))
            )
            self.classifier = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(64, 128),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3),
                nn.Linear(128, 64),
                nn.ReLU(inplace=True),
                nn.Linear(64, num_classes)
            )
        
        def forward(self, x):
            x = self.features(x)
            x = x.view(x.size(0), -1)
            x = self.classifier(x)
            return x

    # New ResNet-based Model
    class ResNetClassifier(nn.Module):
        def __init__(self, num_classes=2, pretrained=True, resnet_type='resnet50'):
            super(ResNetClassifier, self).__init__()
            
            # Choose ResNet architecture
            if resnet_type == 'resnet18':
                self.backbone = models.resnet18(pretrained=pretrained)
                num_features = 512
            elif resnet_type == 'resnet34':
                self.backbone = models.resnet34(pretrained=pretrained)
                num_features = 512
            elif resnet_type == 'resnet50':
                self.backbone = models.resnet50(pretrained=pretrained)
                num_features = 2048
            elif resnet_type == 'resnet101':
                self.backbone = models.resnet101(pretrained=pretrained)
                num_features = 2048
            elif resnet_type == 'resnet152':
                self.backbone = models.resnet152(pretrained=pretrained)
                num_features = 2048
            else:
                raise ValueError(f"Unsupported ResNet type: {resnet_type}")
            
            # Replace the final fully connected layer
            self.backbone.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_features, 512),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3),
                nn.Linear(512, 256),
                nn.ReLU(inplace=True),
                nn.Dropout(0.2),
                nn.Linear(256, num_classes)
            )
        
        def forward(self, x):
            return self.backbone(x)
else:
    # Dummy classes when torch is not available
    class LightweightCNN:
        pass
    class ResNetClassifier:
        pass

# Global ML predictor
ml_model = None
ml_transform = None
device = None
model_type = None
#e

def load_ml_model():
    global ml_model, ml_transform, device, model_type
    if ml_model is not None:
        return True
    
    if not TORCH_AVAILABLE:
        return False
    
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Try to find model files - prioritize ResNet models
        resnet_model_paths = [
            ("best_resnet_model.pth", "resnet50"),
            ("resnet50_classifier_full_data.pth", "resnet50"),
            ("resnet18_classifier_full_data.pth", "resnet18"),
            ("resnet34_classifier_full_data.pth", "resnet34"),
            ("resnet101_classifier_full_data.pth", "resnet101"),
            ("resnet152_classifier_full_data.pth", "resnet152"),
        ]
        
        # Legacy model paths
        legacy_model_paths = ["best_model_resnet.pth", "best.pth", "lightweight_classifier.pth"]
        
        model_loaded = False
        
        # First try to load ResNet models
        for path, resnet_type in resnet_model_paths:
            if os.path.exists(path):
                try:
                    ml_model = ResNetClassifier(num_classes=2, pretrained=False, resnet_type=resnet_type).to(device)
                    ml_model.load_state_dict(torch.load(path, map_location=device))
                    ml_model.eval()
                    model_type = "resnet"
                    print(f"✅ ResNet model loaded from {path} (architecture: {resnet_type})")
                    model_loaded = True
                    break
                except Exception as e:
                    print(f"⚠️ Failed to load ResNet model from {path}: {e}")
                    continue
        
        # If no ResNet model found, try legacy models
        if not model_loaded:
            for path in legacy_model_paths:
                if os.path.exists(path):
                    try:
                        ml_model = LightweightCNN().to(device)
                        ml_model.load_state_dict(torch.load(path, map_location=device))
                        ml_model.eval()
                        model_type = "lightweight"
                        print(f"✅ Lightweight CNN model loaded from {path}")
                        model_loaded = True
                        break
                    except Exception as e:
                        print(f"⚠️ Failed to load legacy model from {path}: {e}")
                        continue
        
        if not model_loaded:
            print("⚠️ No ML model found, using default labels")
            ml_model = None
            return False
        
        # We don't use ml_transform anymore since we do manual preprocessing
        # This avoids the numpy compatibility issue
        ml_transform = None
        
        print("✅ Model classes: 0=gradient, 1=normal")
        print(f"✅ Using manual preprocessing to avoid numpy compatibility issues")
        return True
        
    except Exception as e:
        print(f"❌ Error loading ML model: {e}")
        ml_model = None
        return False

import numpy as np

import numpy as np

def predict_ml_label(image_path):
    global ml_model, ml_transform, device, model_type
    
    if ml_model is None:
        if not load_ml_model():
            return 0, 0.5  # Default: normal, low confidence
    
    try:
        image = Image.open(image_path).convert('RGB')
        
        if model_type == "resnet":
            # For ResNet models, resize to 224x224
            image = image.resize((224, 224), Image.Resampling.LANCZOS)
        else:
            # For legacy models, resize to 256x256
            image = image.resize((256, 256), Image.Resampling.LANCZOS)
        
        # Try multiple approaches to create tensor
        image_tensor = None
        
        # Method 1: Try using torch.tensor with .tolist()
        try:
            np_array = np.asarray(image, dtype=np.float32) / 255.0
            image_tensor = torch.tensor(np_array.tolist(), dtype=torch.float32)
            image_tensor = image_tensor.permute(2, 0, 1)  # HWC to CHW
            print("✅ Used method 1: numpy.tolist()")
        except Exception as e1:
            print(f"⚠️ Method 1 failed: {e1}")
            
            # Method 2: Manual pixel extraction
            try:
                width, height = image.size
                pixels = list(image.getdata())
                
                # Create tensor from raw pixel data
                pixel_tensor = torch.tensor(pixels, dtype=torch.float32) / 255.0
                image_tensor = pixel_tensor.view(height, width, 3).permute(2, 0, 1)
                print("✅ Used method 2: manual pixel extraction")
            except Exception as e2:
                print(f"⚠️ Method 2 failed: {e2}")
                
                # Method 3: Channel-by-channel extraction
                try:
                    width, height = image.size
                    channels = []
                    
                    for c in range(3):  # RGB channels
                        channel_data = []
                        for y in range(height):
                            row = []
                            for x in range(width):
                                pixel = image.getpixel((x, y))
                                row.append(pixel[c] / 255.0)
                            channel_data.append(row)
                        channels.append(channel_data)
                    
                    image_tensor = torch.tensor(channels, dtype=torch.float32)
                    print("✅ Used method 3: channel-by-channel")
                except Exception as e3:
                    print(f"❌ All methods failed: {e1}, {e2}, {e3}")
                    return 0, 0.5
        
        if image_tensor is None:
            print("❌ Failed to create tensor")
            return 0, 0.5
        
        # Apply normalization
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        image_tensor = (image_tensor - mean) / std
        
        # Add batch dimension and move to device
        image_tensor = image_tensor.unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = ml_model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
        
        # Class mapping: predicted_class 0 = gradient, predicted_class 1 = normal
        # Return: 1 for gradient, 0 for normal
        ml_label = 0 if predicted_class == 0 else 1
        
        class_name = "gradient" if predicted_class == 0 else "normal"
        print(f"✅ ML Prediction ({model_type}): {class_name} (model_class={predicted_class}) -> ml_label={ml_label}, Confidence={confidence:.3f}")
        
        return int(ml_label), float(confidence)
        
    except Exception as e:
        print(f"❌ ML prediction error: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0.5
def extract_layers(file_path, output_dir, output_format='PNG', quality=100, display_max_dimension=3000, optimize=True):
    """
    Extract layers from image files - simplified and robust version
    """
    import os
    import json
    from PIL import Image
    import numpy as np
    
    print(f"🔍 EXTRACT_LAYERS: Starting extraction")
    print(f"🔍 EXTRACT_LAYERS: File: {file_path}")
    print(f"🔍 EXTRACT_LAYERS: Output dir: {output_dir}")
    print(f"🔍 EXTRACT_LAYERS: File exists: {os.path.exists(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"❌ EXTRACT_LAYERS: File does not exist!")
        return []
    
    # Load ML model
    load_ml_model()
    
    # Increase PIL's maximum image size limit
    Image.MAX_IMAGE_PIXELS = 500000000
    
    # Get file info
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    file_extension = os.path.splitext(file_path)[1].lower()
    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    
    print(f"🔍 EXTRACT_LAYERS: File size: {file_size_mb:.2f}MB")
    print(f"🔍 EXTRACT_LAYERS: Extension: {file_extension}")
    print(f"🔍 EXTRACT_LAYERS: Base filename: {base_filename}")
    
    # Adjust display size for large files
    if file_size_mb > 50:
        display_max_dimension = display_max_dimension
    elif file_size_mb > 100:
        display_max_dimension = display_max_dimension
    elif file_size_mb > 200:
        display_max_dimension = display_max_dimension
    
    print(f"🔍 EXTRACT_LAYERS: Max display dimension: {display_max_dimension}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    print(f"🔍 EXTRACT_LAYERS: Output directory created/verified: {output_dir}")
    
    layers_info = []
    
    try:
        if file_extension in ['.tiff', '.tif']:
            print(f"🔍 EXTRACT_LAYERS: Processing as TIFF file")
            layers_info = process_tiff_file(file_path, output_dir, base_filename, display_max_dimension, output_format, quality)
        
        elif file_extension in ['.jpg', '.jpeg', '.png']:
            print(f"🔍 EXTRACT_LAYERS: Processing as {file_extension.upper()} file")
            layers_info = process_single_image_file(file_path, output_dir, base_filename, display_max_dimension, output_format, quality)
        
        else:
            print(f"❌ EXTRACT_LAYERS: Unsupported file format: {file_extension}")
            return []
        
        print(f"🔍 EXTRACT_LAYERS: Successfully processed {len(layers_info)} layers")
        for i, layer in enumerate(layers_info):
            ml_label = layer.get('ml_label', 0)
            confidence = layer.get('ml_confidence', 0.0)
            label_text = "gradient" if ml_label == 1 else "normal"
            print(f"🔍 EXTRACT_LAYERS: Layer {i+1}: {layer['name']} - {layer['width']}x{layer['height']} - ML: {label_text} ({confidence:.3f})")
        
        return layers_info
        
    except Exception as e:
        print(f"❌ EXTRACT_LAYERS: Error processing file: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def process_single_image_file(file_path, output_dir, base_filename, display_max_dimension, output_format, quality):
    """Process JPG/PNG files as single layer"""
    from PIL import Image
    import os
    import json
    
    print(f"🔍 PROCESS_SINGLE: Starting with {file_path}")
    
    try:
        # Open the image
        with Image.open(file_path) as img:
            original_width, original_height = img.size
            print(f"🔍 PROCESS_SINGLE: Original dimensions: {original_width}x{original_height}")
            
            # Get DPI info and handle Fraction objects
            dpi_raw = img.info.get('dpi', (300, 300))
            print(f"🔍 PROCESS_SINGLE: Raw DPI: {dpi_raw} (type: {type(dpi_raw)})")
            
            # Convert DPI to integers, handling Fraction objects
            try:
                if isinstance(dpi_raw, (tuple, list)) and len(dpi_raw) == 2:
                    dpi_x = float(dpi_raw[0]) if hasattr(dpi_raw[0], 'numerator') else float(dpi_raw[0])
                    dpi_y = float(dpi_raw[1]) if hasattr(dpi_raw[1], 'numerator') else float(dpi_raw[1])
                    dpi = (int(dpi_x), int(dpi_y))
                else:
                    dpi = (300, 300)  # fallback
            except Exception as dpi_error:
                print(f"⚠️ PROCESS_SINGLE: DPI conversion error: {dpi_error}")
                dpi = (300, 300)  # fallback
            
            print(f"🔍 PROCESS_SINGLE: Converted DPI: {dpi}")
            
            # Calculate physical size
            physical_width_inches = original_width / dpi[0]
            physical_height_inches = original_height / dpi[1]
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P') and output_format.upper() == 'JPEG':
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img)
                img = background
            elif img.mode not in ('RGB', 'RGBA', 'L'):
                img = img.convert('RGB')
            
            # Create file paths
            original_output_path = os.path.join(output_dir, f"{base_filename}_original.{output_format.lower()}")
            display_output_path = os.path.join(output_dir, f"{base_filename}.{output_format.lower()}")
            
            print(f"🔍 PROCESS_SINGLE: Original path: {original_output_path}")
            print(f"🔍 PROCESS_SINGLE: Display path: {display_output_path}")
            
            # Save original version
            img.save(original_output_path, output_format, quality=quality, dpi=dpi)
            print(f"🔍 PROCESS_SINGLE: Saved original version")
            
            # Create display version (resized if needed)
            display_img = img.copy()
            if original_width > display_max_dimension or original_height > display_max_dimension:
                if original_width > original_height:
                    new_width = display_max_dimension
                    new_height = int((original_height * display_max_dimension) / original_width)
                else:
                    new_height = display_max_dimension
                    new_width = int((original_width * display_max_dimension) / original_height)
                
                display_img = display_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"🔍 PROCESS_SINGLE: Resized to: {new_width}x{new_height}")
            else:
                new_width, new_height = original_width, original_height
                print(f"🔍 PROCESS_SINGLE: No resize needed")
            
            # Save display version
            display_img.save(display_output_path, output_format, quality=quality, dpi=dpi)
            print(f"🔍 PROCESS_SINGLE: Saved display version")
            
            # 🤖 ML PREDICTION
            ml_label, confidence = predict_ml_label(display_output_path)
            label_text = "gradient" if ml_label == 1 else "normal"
            print(f"🤖 PROCESS_SINGLE: ML Prediction: {label_text} (confidence: {confidence:.3f})")
            
            # Save metadata - ensure all values are JSON serializable
            metadata = {
                'original_width': int(original_width),
                'original_height': int(original_height),
                'display_width': int(new_width),
                'display_height': int(new_height),
                'dpi_x': int(dpi[0]),
                'dpi_y': int(dpi[1]),
                'physical_width_inches': float(physical_width_inches),
                'physical_height_inches': float(physical_height_inches),
                'ml_label': int(ml_label),
                'ml_confidence': float(confidence),
                'original_path': str(original_output_path),
                'display_path': str(display_output_path),
                'model_type': str(model_type) if model_type else "unknown"
            }
            
            print(f"🔍 PROCESS_SINGLE: Metadata prepared: {metadata}")
            
            metadata_path = os.path.join(output_dir, f"{base_filename}.metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"🔍 PROCESS_SINGLE: Saved metadata")
            
            # Create layer info - ensure all values are the right type
            layer_info = {
                'name': str(base_filename),
                'path': str(display_output_path),
                'original_path': str(original_output_path),
                'layer_position_from_top': 0,
                'layer_position_from_left': 0,
                'width': int(new_width),
                'height': int(new_height),
                'original_width': int(original_width),
                'original_height': int(original_height),
                'dpi_x': int(dpi[0]),
                'dpi_y': int(dpi[1]),
                'physical_width_inches': float(physical_width_inches),
                'physical_height_inches': float(physical_height_inches),
                'ml_label': int(ml_label),
                'ml_confidence': float(confidence)
            }
            
            print(f"🔍 PROCESS_SINGLE: Created layer info: {layer_info}")
            print(f"🔍 PROCESS_SINGLE: Returning 1 layer")
            return [layer_info]
            
    except Exception as e:
        print(f"❌ PROCESS_SINGLE: Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def process_tiff_file(file_path, output_dir, base_filename, display_max_dimension, output_format, quality):
    """Process TIFF files (can have multiple pages/layers)"""
    import tifffile
    from PIL import Image
    import numpy as np
    import os
    import json
    
    print(f"🔍 PROCESS_TIFF: Starting with {file_path}")
    
    layers_info = []
    
    try:
        with tifffile.TiffFile(file_path) as tif:
            n_pages = len(tif.pages)
            print(f"🔍 PROCESS_TIFF: Found {n_pages} pages")
            
            for i, page in enumerate(tif.pages):
                try:
                    print(f"🔍 PROCESS_TIFF: Processing page {i+1}/{n_pages}")
                    
                    # Get image data
                    image_data = page.asarray()
                    original_width = page.imagewidth
                    original_height = page.imagelength
                    
                    print(f"🔍 PROCESS_TIFF: Page {i+1} dimensions: {original_width}x{original_height}")
                    print(f"🔍 PROCESS_TIFF: Page {i+1} array shape: {image_data.shape}")
                    print(f"🔍 PROCESS_TIFF: Page {i+1} array dtype: {image_data.dtype}")
                    
                    # Get DPI from TIFF page and handle Fraction objects
                    dpi = [300, 300]  # default as list to ensure we can modify
                    try:
                        if 'XResolution' in page.tags and 'YResolution' in page.tags:
                            x_res = page.tags['XResolution'].value
                            y_res = page.tags['YResolution'].value
                            
                            print(f"🔍 PROCESS_TIFF: Raw resolution - X: {x_res} (type: {type(x_res)}), Y: {y_res} (type: {type(y_res)})")
                            
                            # Handle different resolution formats
                            if isinstance(x_res, tuple) and len(x_res) == 2:
                                x_dpi = float(x_res[0]) / float(x_res[1])
                            elif hasattr(x_res, 'numerator'):  # Fraction object
                                x_dpi = float(x_res)
                            else:
                                x_dpi = float(x_res)
                                
                            if isinstance(y_res, tuple) and len(y_res) == 2:
                                y_dpi = float(y_res[0]) / float(y_res[1])
                            elif hasattr(y_res, 'numerator'):  # Fraction object
                                y_dpi = float(y_res)
                            else:
                                y_dpi = float(y_res)
                            
                            dpi = [int(x_dpi), int(y_dpi)]
                            print(f"🔍 PROCESS_TIFF: Page {i+1} converted DPI: {dpi}")
                    except Exception as dpi_error:
                        print(f"⚠️ PROCESS_TIFF: Could not get DPI for page {i+1}: {dpi_error}")
                        dpi = [300, 300]  # fallback
                    
                    # Convert numpy array to PIL Image
                    if image_data.dtype == np.float32 or image_data.dtype == np.float64:
                        image_data = (image_data * 255).astype(np.uint8)
                    elif image_data.dtype == bool:
                        image_data = image_data.astype(np.uint8) * 255
                    
                    # Handle different array shapes
                    if len(image_data.shape) == 2:  # Grayscale
                        img = Image.fromarray(image_data, 'L')
                    elif len(image_data.shape) == 3:
                        if image_data.shape[2] == 3:  # RGB
                            img = Image.fromarray(image_data, 'RGB')
                        elif image_data.shape[2] == 4:  # RGBA
                            img = Image.fromarray(image_data, 'RGBA')
                        else:
                            print(f"⚠️ PROCESS_TIFF: Unexpected channels: {image_data.shape[2]}, converting to RGB")
                            img = Image.fromarray(image_data[:,:,:3], 'RGB')
                    else:
                        print(f"❌ PROCESS_TIFF: Unexpected array shape: {image_data.shape}")
                        continue
                    
                    print(f"🔍 PROCESS_TIFF: Page {i+1} converted to PIL image: {img.mode}")
                    
                    # Convert for JPEG if needed
                    if output_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'RGBA':
                            background.paste(img, mask=img.split()[3])
                        else:
                            background.paste(img)
                        img = background
                        print(f"🔍 PROCESS_TIFF: Page {i+1} converted to RGB for JPEG")
                    
                    # Create layer name
                    layer_name = f"layer_{i+1}"
                    try:
                        if hasattr(page, 'description') and page.description:
                            better_name = page.description.strip()
                            if better_name:
                                layer_name = better_name
                                print(f"🔍 PROCESS_TIFF: Using description as layer name: {layer_name}")
                    except:
                        pass
                    
                    # Create file paths
                    original_output_path = os.path.join(output_dir, f"{layer_name}_original.{output_format.lower()}")
                    display_output_path = os.path.join(output_dir, f"{layer_name}.{output_format.lower()}")
                    
                    print(f"🔍 PROCESS_TIFF: Page {i+1} paths:")
                    print(f"    Original: {original_output_path}")
                    print(f"    Display: {display_output_path}")
                    
                    # Save original version
                    img.save(original_output_path, output_format, quality=quality, dpi=tuple(dpi))
                    print(f"🔍 PROCESS_TIFF: Page {i+1} saved original")
                    
                    # Create display version
                    display_img = img.copy()
                    if original_width > display_max_dimension or original_height > display_max_dimension:
                        if original_width > original_height:
                            new_width = display_max_dimension
                            new_height = int((original_height * display_max_dimension) / original_width)
                        else:
                            new_height = display_max_dimension
                            new_width = int((original_width * display_max_dimension) / original_height)
                        
                        display_img = display_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        print(f"🔍 PROCESS_TIFF: Page {i+1} resized to: {new_width}x{new_height}")
                    else:
                        new_width, new_height = original_width, original_height
                        print(f"🔍 PROCESS_TIFF: Page {i+1} no resize needed")
                    
                    # Save display version
                    display_img.save(display_output_path, output_format, quality=quality, dpi=tuple(dpi))
                    print(f"🔍 PROCESS_TIFF: Page {i+1} saved display")
                    
                    # 🤖 ML PREDICTION
                    ml_label, confidence = predict_ml_label(display_output_path)
                    label_text = "gradient" if ml_label == 1 else "normal"
                    print(f"🤖 PROCESS_TIFF: Page {i+1} ML Prediction: {label_text} (confidence: {confidence:.3f})")
                    
                    # Calculate physical size
                    physical_width_inches = float(original_width) / float(dpi[0])
                    physical_height_inches = float(original_height) / float(dpi[1])
                    
                    # Save metadata - ensure all values are JSON serializable
                    metadata = {
                        'original_width': int(original_width),
                        'original_height': int(original_height),
                        'display_width': int(new_width),
                        'display_height': int(new_height),
                        'dpi_x': int(dpi[0]),
                        'dpi_y': int(dpi[1]),
                        'physical_width_inches': float(physical_width_inches),
                        'physical_height_inches': float(physical_height_inches),
                        'ml_label': int(ml_label),
                        'ml_confidence': float(confidence),
                        'original_path': str(original_output_path),
                        'display_path': str(display_output_path),
                        'model_type': str(model_type) if model_type else "unknown"
                    }
                    
                    metadata_path = os.path.join(output_dir, f"{layer_name}.metadata.json")
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    print(f"🔍 PROCESS_TIFF: Page {i+1} saved metadata")
                    
                    # Create layer info - ensure all values are the right type
                    layer_info = {
                        'name': str(layer_name),
                        'path': str(display_output_path),
                        'original_path': str(original_output_path),
                        'layer_position_from_top': 0,
                        'layer_position_from_left': 0,
                        'width': int(new_width),
                        'height': int(new_height),
                        'original_width': int(original_width),
                        'original_height': int(original_height),
                        'dpi_x': int(dpi[0]),
                        'dpi_y': int(dpi[1]),
                        'physical_width_inches': float(physical_width_inches),
                        'physical_height_inches': float(physical_height_inches),
                        'ml_label': int(ml_label),
                        'ml_confidence': float(confidence)
                    }
                    
                    layers_info.append(layer_info)
                    print(f"🔍 PROCESS_TIFF: Page {i+1} added to layers_info")
                    
                except Exception as page_error:
                    print(f"❌ PROCESS_TIFF: Error processing page {i+1}: {str(page_error)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"🔍 PROCESS_TIFF: Completed processing {len(layers_info)} layers")
            return layers_info
            
    except Exception as e:
        print(f"❌ PROCESS_TIFF: Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []
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