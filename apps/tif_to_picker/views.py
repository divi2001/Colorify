# apps\tif_to_picker\views.py
import os
import psdtags
import numpy as np
from PIL import Image
from collections import Counter
from psdtags import PsdChannelId
from .forms import TiffUploadForm
from django.shortcuts import render
from psdtags.psdtags import TiffImageSourceData, PsdChannelId
from tifffile import TiffFile, imshow,imwrite,imsave
from matplotlib import pyplot
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings
import os
from PIL import Image
import json
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import io
from PIL import Image
from django.views import View
import colorsys
from typing import Dict, List, Optional

from colorsys import rgb_to_hls
import base64

import imagecodecs
from PIL import ImageOps
import cv2
import logging
from .getcolors import analyze_image_colors
from io import BytesIO

logger = logging.getLogger(__name__)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from apps.subscription_module.models import InspirationPDF,PDFLike


from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from apps.subscription_module.models import Palette
from apps.subscription_module.serializers import PaletteSerializer
import tifffile
from PIL import Image
import numpy as np
import os
import json
import base64
import io
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from apps.core.models import Project

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


def upload_tiff(request, user_id=None, project_id=None):
    # Handle project editing case
    project = None
    if user_id and project_id:
        project = get_object_or_404(Project, id=project_id, user_id=user_id)
    
    if request.method == 'POST':
        form = TiffUploadForm(request.POST, request.FILES)
        if form.is_valid():
            tiff_file = request.FILES['tiff_file']
            # Create a better file path that includes project_id if available
            filename = f"project_{project_id}_{tiff_file.name}" if project else tiff_file.name
            file_path = os.path.join('media', 'uploads', filename)

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'wb+') as destination:
                for chunk in tiff_file.chunks():
                    destination.write(chunk)
            
            # Process the file
            output_dir = os.path.join('media', 'output', str(project_id) if project else 'demo')
            layers = extract_layers(file_path, output_dir)
            
            # Convert paths to use MEDIA_URL
            for layer in layers:
                # Make path relative to media directory
                rel_path = layer['path'].replace('\\', '/').split('media/')[-1]
                layer['path'] = os.path.join(settings.MEDIA_URL, rel_path)

            with Image.open(file_path) as img:
                width, height = img.size
            
            context = {
                'layer_count': len(layers),
                'layers': layers,
                'width': width,
                'height': height,
                'MEDIA_URL': settings.MEDIA_URL  # Pass this to template
            }
            
            if project:
                context.update({
                    'user': request.user,
                    'project': project,
                    'is_edit_mode': True
                })
            
            return render(request, 'layers.html', context)
    else:
        form = TiffUploadForm()
    
    context = {'form': form}
    if project:
        context.update({
            'is_edit_mode': True,
            'project': project
        })
    
    return render(request, 'upload.html', context)

@csrf_exempt
def export_tiff(request):
    if request.method == 'POST':
        try:
            layers_data = json.loads(request.POST.get('layers_data', '[]'))
            output_path = os.path.join('media', 'exported_tiff', f'output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.tif')
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            processed_layers = []
            
            # Find canvas dimensions based on all layers
            max_width = 0
            max_height = 0
            
            # First pass: process layers and determine canvas size
            for layer_data in layers_data:
                try:
                    base64_str = layer_data['imageData'].split(',')[1]
                    img_data = base64.b64decode(base64_str)
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Get original DPI if available
                    dpi = img.info.get('dpi', (300, 300))
                    
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    left_pos = int(layer_data['position_left'])
                    top_pos = int(layer_data['position_top'])
                    width = img.width  # Use original width
                    height = img.height  # Use original height
                    
                    # Update maximum dimensions
                    max_width = max(max_width, left_pos + width)
                    max_height = max(max_height, top_pos + height)
                    
                    metadata = {
                        'Name': layer_data['name'],
                        'TopPosition': top_pos,
                        'LeftPosition': left_pos,
                        'Width': width,
                        'Height': height,
                        'DPI': dpi,
                        'OriginalWidth': width,
                        'OriginalHeight': height
                    }
                    
                    # Store both PIL Image and numpy array
                    processed_layers.append({
                        'image': img,
                        'data': np.array(img),
                        'metadata': metadata
                    })
                    
                except Exception as e:
                    print(f"Error processing layer {layer_data['name']}: {str(e)}")
                    continue

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
            
            composite_array = np.array(composite_image)
            
            # Get the highest DPI from all layers for the composite
            max_dpi = (300, 300)  # default
            for layer in processed_layers:
                layer_dpi = layer['metadata']['DPI']
                max_dpi = (max(max_dpi[0], layer_dpi[0]), max(max_dpi[1], layer_dpi[1]))
            
            composite_metadata = {
                'Name': 'Composite View',
                'Width': max_width,
                'Height': max_height,
                'LayerCount': len(processed_layers),
                'LayerNames': [layer['metadata']['Name'] for layer in processed_layers],
                'IsComposite': True,
                'DPI': max_dpi
            }
            
            # Write multi-page TIFF
            with tifffile.TiffWriter(output_path) as tif:
                # Write composite as first page
                tif.write(
                    composite_array,
                    photometric='rgb',
                    planarconfig='contig',
                    metadata=composite_metadata,
                    compression='adobe_deflate',
                    resolutionunit='INCH',
                    resolution=max_dpi,  # Use maximum DPI for composite
                    description='Composite View'
                )
                
                # Write individual layers
                for layer in processed_layers:
                    layer_full = np.zeros((max_height, max_width, 4), dtype=np.uint8)
                    h, w = layer['data'].shape[:2]
                    top = layer['metadata']['TopPosition']
                    left = layer['metadata']['LeftPosition']
                    layer_full[top:top+h, left:left+w] = layer['data']
                    
                    # Use original DPI for each layer
                    layer_dpi = layer['metadata']['DPI']
                    
                    tif.write(
                        layer_full,
                        photometric='rgb',
                        planarconfig='contig',
                        metadata=layer['metadata'],
                        compression='adobe_deflate',
                        resolutionunit='INCH',
                        resolution=layer_dpi,  # Use original DPI for each layer
                        description=layer['metadata']['Name']
                    )

            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='image/tiff')
                response['Content-Disposition'] = f'attachment; filename="exported_{datetime.now().strftime("%Y%m%d_%H%M%S")}.tif"'
                return response

        except Exception as e:
            error_msg = f"Export error: {str(e)}"
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

import os
import numpy as np
from matplotlib import pyplot
from psdtags.psdtags import TiffImageSourceData, PsdChannelId, PsdKey
import struct

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

def extract_layers(file_path, output_dir, output_format='PNG', quality=85, max_dimension=4000, optimize=True):
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
    from PIL import Image
    import os
    import numpy as np
    from matplotlib import pyplot
    import piexif
    from PIL.Image import Resampling
    
    # Increase PIL's maximum image size limit
    Image.MAX_IMAGE_PIXELS = None  # Disable the decompression bomb warning
    
    def compress_and_save_image(image_array, output_path, original_size=None):
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

            # Get original dimensions
            orig_width, orig_height = img.size
            print(f"Original dimensions: {orig_width}x{orig_height}")

            # Resize if max_dimension is specified and image exceeds it
            if max_dimension and (orig_width > max_dimension or orig_height > max_dimension):
                if orig_width > orig_height:
                    new_width = max_dimension
                    new_height = int((orig_height * max_dimension) / orig_width)
                else:
                    new_height = max_dimension
                    new_width = int((orig_width * max_dimension) / orig_height)
                
                print(f"Resizing to: {new_width}x{new_height}")
                img = img.resize((new_width, new_height), Resampling.LANCZOS)

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
                    img.save(output_path, 
                           'PNG',
                           optimize=optimize,
                           compress_level=9)
                elif output_format.upper() == 'JPEG':
                    img.save(output_path, 
                           'JPEG',
                           quality=quality,
                           optimize=optimize,
                           progressive=True)
                elif output_format.upper() == 'WEBP':
                    img.save(output_path, 
                           'WEBP',
                           quality=quality,
                           method=6,  # Highest compression method
                           lossless=False)
                else:
                    raise ValueError(f"Unsupported output format: {output_format}")

                # Print compression stats if original size is provided
                if original_size:
                    new_size = os.path.getsize(output_path)
                    reduction = ((original_size - new_size) / original_size) * 100
                    print(f"Size reduced by {reduction:.1f}% ({original_size/1024/1024:.1f}MB -> {new_size/1024/1024:.1f}MB)")

                return img.size

            except Exception as save_error:
                print(f"Error saving image: {str(save_error)}")
                if os.path.exists(output_path):
                    os.remove(output_path)  # Clean up partial file
                return None

        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None

    # Check file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension in ['.jpg', '.jpeg', '.png']:
        # Handle JPEG/PNG files
        try:
            original_size = os.path.getsize(file_path)
            with Image.open(file_path) as img:
                full_image = np.array(img)
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            base_filename = os.path.splitext(os.path.basename(file_path))[0]
            layer_output_path = os.path.join(output_dir, f"{base_filename}.{output_format.lower()}")
            
            size = compress_and_save_image(full_image, layer_output_path, original_size)
            if size is None:
                return []
            
            width, height = size
            return [{
                'name': base_filename,
                'path': layer_output_path,
                'layer_position_from_top': 0,
                'layer_position_from_left': 0,
                'width': width,
                'height': height
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
                original_size = os.path.getsize(file_path) // n_pages  # Approximate size per layer
                
                print(f"Processing TIFF file with {n_pages} pages")
                
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                layers_info = []
                
                # Process each page as a layer
                for i, page in enumerate(tif.pages, 1):
                    try:
                        # Get the image data
                        image = page.asarray()
                        
                        # Create layer name
                        layer_name = f"layer_{i}"
                        
                        # Create output path
                        layer_output_path = os.path.join(output_dir, f"{layer_name}.{output_format.lower()}")
                        
                        print(f"Processing layer {i}/{n_pages}: {layer_name}")
                        
                        # Compress and save the image
                        size = compress_and_save_image(image, layer_output_path, original_size)
                        if size is None:
                            continue
                        
                        width, height = size
                        
                        # Add layer info
                        layers_info.append({
                            'name': layer_name,
                            'path': layer_output_path,
                            'layer_position_from_top': 0,
                            'layer_position_from_left': 0,
                            'width': width,
                            'height': height
                        })
                        
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