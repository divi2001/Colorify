import os
import numpy as np
import tifffile
from PIL import Image, ExifTags
import json
import struct
from fractions import Fraction
import piexif
from PIL.Image import Resampling
import gc
import signal
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def extract_layers(file_path, output_dir, output_format='PNG', quality=100, display_max_dimension=1200, optimize=True, max_file_size_mb=100):
    """
    Extract layers from image files, creating both original and display versions.
    Handles large files with chunked processing and memory optimization.
    
    Parameters:
    file_path (str): Path to input image file (TIFF, JPEG, PNG)
    output_dir (str): Directory to save extracted layers
    output_format (str): Output format ('PNG', 'JPEG', 'WEBP')
    quality (int): Compression quality (1-100) for JPEG/WEBP
    display_max_dimension (int): Maximum dimension for display version (maintains aspect ratio)
    optimize (bool): Apply additional optimization
    max_file_size_mb (int): Threshold for chunked processing
    """
    
    # Increase PIL's maximum image size limit
    Image.MAX_IMAGE_PIXELS = None
    
    # Check file size first
    try:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"Processing file: {file_path} ({file_size_mb:.1f}MB)")
        
        if file_size_mb > max_file_size_mb:
            print(f"Large file detected ({file_size_mb:.1f}MB), using optimized processing")
            return extract_layers_optimized(file_path, output_dir, output_format, quality, 
                                           min(display_max_dimension, 800), optimize)
    except Exception as e:
        print(f"Error checking file size: {str(e)}")
        return []
    
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
    
    def save_image_version(image_array, output_path, original_size=None, dpi=(300, 300), 
                          physical_size_inches=None, is_display_version=False, 
                          original_dimensions=None, max_memory_mb=200):
        """Save image with proper metadata, handling both original and display versions"""
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

            # Store original dimensions before any processing
            if original_dimensions is None:
                original_dimensions = img.size
            
            # Check memory usage and adjust if necessary
            width, height = img.size
            channels = len(img.getbands())
            memory_mb = (width * height * channels) / (1024 * 1024)
            
            if memory_mb > max_memory_mb and is_display_version:
                # Further reduce size if memory usage is too high
                reduction_factor = (max_memory_mb / memory_mb) ** 0.5
                new_max_dim = int(display_max_dimension * reduction_factor)
                print(f"Reducing display size due to memory constraints: {new_max_dim}")
                display_max_dimension = new_max_dim
            
            # For display version, resize if needed
            if is_display_version and display_max_dimension:
                orig_width, orig_height = img.size
                if orig_width > display_max_dimension or orig_height > display_max_dimension:
                    if orig_width > orig_height:
                        new_width = display_max_dimension
                        new_height = int((orig_height * display_max_dimension) / orig_width)
                    else:
                        new_height = display_max_dimension
                        new_width = int((orig_width * display_max_dimension) / orig_height)
                    
                    print(f"Resizing display version to: {new_width}x{new_height}")
                    img = img.resize((new_width, new_height), Resampling.LANCZOS)
                    
                    # Recalculate DPI for display version to maintain physical size
                    if physical_size_inches:
                        physical_width_inches, physical_height_inches = physical_size_inches
                        new_x_dpi = new_width / physical_width_inches
                        new_y_dpi = new_height / physical_height_inches
                        display_dpi = (int(new_x_dpi), int(new_y_dpi))
                        print(f"Display version DPI: {display_dpi}")
                    else:
                        display_dpi = dpi
                else:
                    display_dpi = dpi
            else:
                display_dpi = dpi
            
            # Get current image dimensions after any resizing
            current_width, current_height = img.size
            
            # If we didn't get physical size, calculate it from original DPI
            if physical_size_inches is None:
                physical_width_inches = original_dimensions[0] / dpi[0]
                physical_height_inches = original_dimensions[1] / dpi[1]
                physical_size_inches = (physical_width_inches, physical_height_inches)
            else:
                physical_width_inches, physical_height_inches = physical_size_inches
            
            version_type = "display" if is_display_version else "original"
            print(f"{version_type.capitalize()} version - Current: {current_width}x{current_height}, "
                  f"Original: {original_dimensions[0]}x{original_dimensions[1]}, "
                  f"Physical: {physical_width_inches:.4f}\" × {physical_height_inches:.4f}\"")
            
            # Set ML label to 1 (hardcoded)
            ml_label = 1

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
                save_dpi = display_dpi if is_display_version else dpi
                
                if output_format.upper() == 'PNG':
                    # For PNG, set up the pHYs chunk for DPI
                    ppm_x = int(save_dpi[0] / 0.0254)  # Convert DPI to pixels per meter
                    ppm_y = int(save_dpi[1] / 0.0254)
                    
                    # Create a new PNG info object
                    png_info = None
                    try:
                        from PIL import PngImagePlugin
                        png_info = PngImagePlugin.PngInfo()
                        png_info.add_text("Software", "Python PIL")
                        png_info.add(b'pHYs', struct.pack('>IIB', ppm_x, ppm_y, 1))
                    except:
                        print("Warning: Could not create PNG info")
                    
                    img.save(output_path, 
                           'PNG',
                           optimize=optimize,
                           compress_level=9,
                           dpi=save_dpi,
                           pnginfo=png_info)
                
                elif output_format.upper() == 'JPEG':
                    # JPEG DPI handling
                    def dpi_to_rational(dpi_value):
                        fraction = Fraction(dpi_value).limit_denominator(65535)
                        return (fraction.numerator, fraction.denominator)
                    
                    x_dpi_rational = dpi_to_rational(save_dpi[0])
                    y_dpi_rational = dpi_to_rational(save_dpi[1])
                    
                    img.save(output_path, 
                           'JPEG',
                           quality=quality,
                           optimize=optimize,
                           progressive=True,
                           dpi=save_dpi)
                    
                    # Add EXIF resolution data
                    try:
                        exif_dict = {"0th": {}, "Exif": {}, "1st": {}, "GPS": {}}
                        exif_dict["0th"][piexif.ImageIFD.XResolution] = x_dpi_rational
                        exif_dict["0th"][piexif.ImageIFD.YResolution] = y_dpi_rational
                        exif_dict["0th"][piexif.ImageIFD.ResolutionUnit] = 2  # inches
                        
                        exif_bytes = piexif.dump(exif_dict)
                        piexif.insert(exif_bytes, output_path)
                    except Exception as exif_err:
                        print(f"Warning: Could not add EXIF resolution: {str(exif_err)}")
                
                elif output_format.upper() == 'WEBP':
                    img.save(output_path, 
                           'WEBP',
                           quality=quality,
                           method=6,
                           lossless=False)
                else:
                    raise ValueError(f"Unsupported output format: {output_format}")

                # Print compression stats if original size is provided
                if original_size:
                    new_size = os.path.getsize(output_path)
                    reduction = ((original_size - new_size) / original_size) * 100
                    print(f"{version_type.capitalize()} size: {original_size/1024/1024:.1f}MB -> {new_size/1024/1024:.1f}MB ({reduction:.1f}% reduction)")

                return img.size, original_dimensions, ml_label, save_dpi, physical_size_inches

            except Exception as save_error:
                print(f"Error saving {version_type} image: {str(save_error)}")
                if os.path.exists(output_path):
                    os.remove(output_path)
                return None, None, None, None, None

        except Exception as e:
            print(f"Error processing {version_type if 'is_display_version' in locals() else 'unknown'} image: {str(e)}")
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
                original_dimensions = img.size
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            base_filename = os.path.splitext(os.path.basename(file_path))[0]
            
            # Create both original and display versions
            original_output_path = os.path.join(output_dir, f"{base_filename}_original.{output_format.lower()}")
            display_output_path = os.path.join(output_dir, f"{base_filename}.{output_format.lower()}")
            
            # Save original version (no resizing)
            orig_size, orig_dims, ml_label, orig_dpi, physical_size = save_image_version(
                full_image, original_output_path, original_size, dpi=dpi, 
                physical_size_inches=physical_size_inches, is_display_version=False,
                original_dimensions=original_dimensions
            )
            
            # Save display version (resized)
            display_size, _, _, display_dpi, _ = save_image_version(
                full_image, display_output_path, original_size, dpi=dpi,
                physical_size_inches=physical_size_inches, is_display_version=True,
                original_dimensions=original_dimensions
            )
            
            if display_size is None or orig_size is None:
                return []
            
            display_width, display_height = display_size
            orig_width, orig_height = orig_dims
            physical_width_inches, physical_height_inches = physical_size
            
            # Save metadata
            metadata_path = os.path.join(output_dir, f"{base_filename}.metadata.json")
            metadata = {
                'original_width': orig_width,
                'original_height': orig_height,
                'display_width': display_width,
                'display_height': display_height,
                'dpi_x': orig_dpi[0],
                'dpi_y': orig_dpi[1],
                'physical_width_inches': physical_width_inches,
                'physical_height_inches': physical_height_inches,
                'ml_label': ml_label,
                'original_path': original_output_path,
                'display_path': display_output_path
            }
            
            with open(metadata_path, 'w') as metadata_file:
                json.dump(metadata, metadata_file)
            
            return [{
                'name': base_filename,
                'path': display_output_path,  # Browser uses display version
                'original_path': original_output_path,  # Keep reference to original
                'layer_position_from_top': 0,
                'layer_position_from_left': 0,
                'width': display_width,
                'height': display_height,
                'original_width': orig_width,
                'original_height': orig_height,
                'dpi_x': orig_dpi[0],
                'dpi_y': orig_dpi[1],
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
                n_pages = len(tif.pages)
                original_size = os.path.getsize(file_path) // max(1, n_pages)
                
                print(f"Processing TIFF file with {n_pages} pages")
                
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                layers_info = []
                
                # Process each page as a layer
                for i, page in enumerate(tif.pages, 1):
                    try:
                        # Get the image data
                        image = page.asarray()
                        original_dimensions = (page.imagewidth, page.imagelength)
                        
                        # Extract both DPI and physical dimensions
                        dpi, physical_size_inches = get_dpi_from_tiff_page(page)
                        print(f"Layer {i} - DPI: {dpi}, Physical size: {physical_size_inches}")
                        
                        # Create layer name
                        layer_name = f"layer_{i}"
                        
                        # Try to get better name from metadata
                        try:
                            if hasattr(page, 'description') and page.description:
                                better_name = page.description.strip()
                                if better_name:
                                    layer_name = better_name
                                    print(f"Using description as layer name: {layer_name}")
                        except:
                            pass
                        
                        # Create output paths for both versions
                        original_output_path = os.path.join(output_dir, f"{layer_name}_original.{output_format.lower()}")
                        display_output_path = os.path.join(output_dir, f"{layer_name}.{output_format.lower()}")
                        
                        print(f"Processing layer {i}/{n_pages}: {layer_name}")
                        
                        # Save original version
                        orig_size, orig_dims, ml_label, orig_dpi, physical_size = save_image_version(
                            image, original_output_path, original_size, dpi=dpi,
                            physical_size_inches=physical_size_inches, is_display_version=False,
                            original_dimensions=original_dimensions
                        )
                        
                        # Save display version
                        display_size, _, _, display_dpi, _ = save_image_version(
                            image, display_output_path, original_size, dpi=dpi,
                            physical_size_inches=physical_size_inches, is_display_version=True,
                            original_dimensions=original_dimensions
                        )
                        
                        if display_size is None or orig_size is None:
                            continue
                        
                        display_width, display_height = display_size
                        orig_width, orig_height = orig_dims
                        physical_width_inches, physical_height_inches = physical_size
                        
                        # Save metadata
                        metadata_path = os.path.join(output_dir, f"{layer_name}.metadata.json")
                        metadata = {
                            'original_width': orig_width,
                            'original_height': orig_height,
                            'display_width': display_width,
                            'display_height': display_height,
                            'dpi_x': orig_dpi[0],
                            'dpi_y': orig_dpi[1],
                            'physical_width_inches': physical_width_inches,
                            'physical_height_inches': physical_height_inches,
                            'ml_label': ml_label,
                            'original_path': original_output_path,
                            'display_path': display_output_path
                        }
                        
                        with open(metadata_path, 'w') as metadata_file:
                            json.dump(metadata, metadata_file)
                        
                        # Add layer info
                        layer_info = {
                            'name': layer_name,
                            'path': display_output_path,  # Browser uses display version
                            'original_path': original_output_path,  # Keep reference to original
                            'layer_position_from_top': 0,
                            'layer_position_from_left': 0,
                            'width': display_width,
                            'height': display_height,
                            'original_width': orig_width,
                            'original_height': orig_height,
                            'dpi_x': orig_dpi[0],
                            'dpi_y': orig_dpi[1],
                            'physical_width_inches': physical_width_inches,
                            'physical_height_inches': physical_height_inches,
                            'ml_label': ml_label
                        }
                        
                        layers_info.append(layer_info)
                        
                        # Force garbage collection after each layer
                        del image
                        gc.collect()
                        
                    except Exception as e:
                        print(f"Error processing layer {i}: {str(e)}")
                        continue
                
                return layers_info
                
        except Exception as e:
            print(f"Error processing TIFF file: {str(e)}")
            return []
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")


def extract_layers_optimized(file_path, output_dir, output_format='JPEG', quality=85, display_max_dimension=800, optimize=True):
    """
    Optimized processing for large files with memory management and chunked processing.
    """
    def process_large_image_efficiently(image_data, max_dimension):
        """Process large images with memory optimization"""
        try:
            # If it's a numpy array, convert to PIL immediately for efficient processing
            if isinstance(image_data, np.ndarray):
                if image_data.dtype == np.float32 or image_data.dtype == np.float64:
                    image_data = (image_data * 255).astype(np.uint8)
                
                if len(image_data.shape) == 2:
                    pil_img = Image.fromarray(image_data, 'L')
                elif len(image_data.shape) == 3:
                    if image_data.shape[2] == 3:
                        pil_img = Image.fromarray(image_data, 'RGB')
                    elif image_data.shape[2] == 4:
                        pil_img = Image.fromarray(image_data, 'RGBA')
                    else:
                        pil_img = Image.fromarray(image_data)
                else:
                    pil_img = Image.fromarray(image_data)
            else:
                pil_img = image_data
            
            # Calculate new size maintaining aspect ratio
            width, height = pil_img.size
            
            # Skip extremely large layers
            if width * height > 100000000:  # 100 megapixels
                print(f"Skipping layer - too large ({width}x{height})")
                return None
            
            if width > max_dimension or height > max_dimension:
                if width > height:
                    new_width = max_dimension
                    new_height = int((height * max_dimension) / width)
                else:
                    new_height = max_dimension
                    new_width = int((width * max_dimension) / height)
                
                print(f"Resizing large image from {width}x{height} to {new_width}x{new_height}")
                
                # Use LANCZOS for high quality downsampling
                resized = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                return resized
            else:
                return pil_img
                
        except Exception as e:
            print(f"Error processing large image: {str(e)}")
            return None
        finally:
            # Clean up
            if 'pil_img' in locals():
                del pil_img
            gc.collect()

    def get_dpi_from_tiff_page_optimized(page):
        """Optimized DPI extraction for large files"""
        default_dpi = (300, 300)
        
        try:
            pixel_width = page.imagewidth
            pixel_height = page.imagelength
            
            if 'XResolution' in page.tags and 'YResolution' in page.tags:
                x_resolution = page.tags['XResolution'].value
                y_resolution = page.tags['YResolution'].value
                
                if isinstance(x_resolution, tuple) and len(x_resolution) == 2:
                    x_dpi = x_resolution[0] / x_resolution[1]
                else:
                    x_dpi = x_resolution
                    
                if isinstance(y_resolution, tuple) and len(y_resolution) == 2:
                    y_dpi = y_resolution[0] / y_resolution[1]
                else:
                    y_dpi = y_resolution
                
                resolution_unit = page.tags.get('ResolutionUnit', 2).value
                if resolution_unit == 3:
                    x_dpi = x_dpi * 2.54
                    y_dpi = y_dpi * 2.54
                
                dpi = (int(x_dpi), int(y_dpi))
                physical_width_inches = pixel_width / x_dpi
                physical_height_inches = pixel_height / y_dpi
                physical_size_inches = (physical_width_inches, physical_height_inches)
                
                return dpi, physical_size_inches
            else:
                physical_width_inches = pixel_width / default_dpi[0]
                physical_height_inches = pixel_height / default_dpi[1]
                physical_size_inches = (physical_width_inches, physical_height_inches)
                return default_dpi, physical_size_inches
                
        except Exception as e:
            print(f"Error getting DPI from TIFF page: {str(e)}")
            return default_dpi, None

    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension in ['.tiff', '.tif']:
            layers_info = []
            
            with tifffile.TiffFile(file_path) as tif:
                n_pages = len(tif.pages)
                print(f"Processing large TIFF with {n_pages} pages using optimized method")
                
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                for i, page in enumerate(tif.pages, 1):
                    try:
                        print(f"Processing layer {i}/{n_pages} (optimized)")
                        
                        # Get dimensions first to check if we should process
                        width, height = page.imagewidth, page.imagelength
                        
                        # Skip extremely large individual layers
                        if width * height > 200000000:  # 200 megapixels
                            print(f"Skipping layer {i} - dimensions too large ({width}x{height})")
                            continue
                        
                        # Get DPI info
                        dpi, physical_size_inches = get_dpi_from_tiff_page_optimized(page)
                        
                        # Load and process image data
                        try:
                            image_data = page.asarray()
                        except Exception as load_error:
                            print(f"Error loading layer {i} data: {str(load_error)}")
                            continue
                        
                        # Process the image efficiently
                        processed_img = process_large_image_efficiently(image_data, display_max_dimension)
                        
                        # Clean up original data immediately
                        del image_data
                        gc.collect()
                        
                        if processed_img is None:
                            continue
                        
                        # Create layer name
                        layer_name = f"layer_{i}"
                        
                        # Only create display version for large files to save space and time
                        display_output_path = os.path.join(output_dir, f"{layer_name}.{output_format.lower()}")
                        
                        try:
                            # Convert color mode if necessary for JPEG
                            if output_format.upper() == 'JPEG' and processed_img.mode in ('RGBA', 'LA', 'P'):
                                background = Image.new('RGB', processed_img.size, (255, 255, 255))
                                if processed_img.mode == 'RGBA':
                                    background.paste(processed_img, mask=processed_img.split()[3])
                                else:
                                    background.paste(processed_img)
                                processed_img = background
                            
                            # Save the processed image
                            if output_format.upper() == 'JPEG':
                                processed_img.save(display_output_path, 'JPEG', 
                                                 quality=quality, optimize=optimize, progressive=True)
                            elif output_format.upper() == 'PNG':
                                processed_img.save(display_output_path, 'PNG', 
                                                 optimize=optimize, compress_level=9)
                            elif output_format.upper() == 'WEBP':
                                processed_img.save(display_output_path, 'WEBP', 
                                                 quality=quality, method=6)
                            
                            # Get final dimensions
                            final_width, final_height = processed_img.size
                            
                            # Calculate physical size
                            if physical_size_inches:
                                physical_width_inches, physical_height_inches = physical_size_inches
                            else:
                                physical_width_inches = width / dpi[0]
                                physical_height_inches = height / dpi[1]
                            
                            # Save minimal metadata for large files
                            metadata_path = os.path.join(output_dir, f"{layer_name}.metadata.json")
                            metadata = {
                                'original_width': width,
                                'original_height': height,
                                'display_width': final_width,
                                'display_height': final_height,
                                'dpi_x': dpi[0],
                                'dpi_y': dpi[1],
                                'physical_width_inches': physical_width_inches,
                                'physical_height_inches': physical_height_inches,
                                'ml_label': 1,
                                'display_path': display_output_path,
                                'large_file_mode': True
                            }
                            
                            with open(metadata_path, 'w') as metadata_file:
                                json.dump(metadata, metadata_file)
                            
                            # Add layer info
                            layer_info = {
                                'name': layer_name,
                                'path': display_output_path,
                                'layer_position_from_top': 0,
                                'layer_position_from_left': 0,
                                'width': final_width,
                                'height': final_height,
                                'original_width': width,
                                'original_height': height,
                                'dpi_x': dpi[0],
                                'dpi_y': dpi[1],
                                'physical_width_inches': physical_width_inches,
                                'physical_height_inches': physical_height_inches,
                                'ml_label': 1
                            }
                            
                            layers_info.append(layer_info)
                            print(f"Successfully processed layer {i}")
                            
                        except Exception as save_error:
                            print(f"Error saving layer {i}: {str(save_error)}")
                            if os.path.exists(display_output_path):
                                os.remove(display_output_path)
                        finally:
                            # Clean up processed image
                            if 'processed_img' in locals():
                                del processed_img
                            gc.collect()
                            
                    except Exception as layer_error:
                        print(f"Error processing layer {i}: {str(layer_error)}")
                        continue
            
            return layers_info
            
        else:
            # For non-TIFF large files, fall back to regular processing with reduced dimensions
            return extract_layers(file_path, output_dir, output_format, quality, 
                                min(display_max_dimension, 600), optimize, 999999)  # Force regular processing
            
    except Exception as e:
        print(f"Error in optimized large file processing: {str(e)}")
        return []


def timeout_handler(signum, frame):
    """Signal handler for processing timeout"""
    raise TimeoutError("File processing timed out")


# Updated upload view function with timeout and error handling
@login_required  
def upload_tiff(request, user_id=None, project_id=None):
    """
    Handles TIFF file uploads with subscription limit enforcement and large file optimization
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
            # Calculate file size in MB
            file_size_bytes = tiff_file.size
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            # Add file size limits
            MAX_FILE_SIZE_MB = 500  # Adjust based on your server capacity
            if file_size_mb > MAX_FILE_SIZE_MB:
                messages.error(request, f"File too large ({file_size_mb:.1f}MB). Maximum allowed: {MAX_FILE_SIZE_MB}MB")
                return redirect(request.path)
            
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
            
            # Set processing timeout based on file size
            timeout_seconds = min(600, max(60, int(precise_file_size_mb * 5)))  # 5 seconds per MB, max 10 minutes
            
            # Set up timeout signal (Unix-like systems only)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)
            
            try:
                # Extract layers with size-based parameters
                if precise_file_size_mb > 50:
                    # For large files, use JPEG and smaller display size
                    layers = extract_layers(file_path, output_dir, 
                                          output_format='JPEG', 
                                          quality=85, 
                                          display_max_dimension=800,
                                          max_file_size_mb=50)
                else:
                    layers = extract_layers(file_path, output_dir)
                
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)  # Cancel timeout
                
            except TimeoutError:
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                if os.path.exists(file_path):
                    os.remove(file_path)
                messages.error(request, f"File processing timed out after {timeout_seconds} seconds. Please try a smaller file or contact support.")
                return redirect(request.path)
            except Exception as e:
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                logger.error(f"Error extracting layers: {e}")
                if os.path.exists(file_path):
                    os.remove(file_path)
                messages.error(request, "Error processing TIFF layers. Please check the file format.")
                return redirect(request.path)
            
            # Convert paths for template
            for layer in layers:
                if 'path' in layer:
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
                'success_message': 'File uploaded successfully!',
                'file_size_mb': precise_file_size_mb
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


