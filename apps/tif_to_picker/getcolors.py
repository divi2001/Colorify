# apps\tif_to_picker\getcolors.py

from PIL import Image
import numpy as np
import logging
import traceback

logger = logging.getLogger(__name__)

def rgb_to_hsl(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    
    l = (max_val + min_val) / 2
    
    if max_val == min_val:
        return 0, 0, l
    
    d = max_val - min_val
    s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
    
    if max_val == r:
        h = (g - b) / d + (6 if g < b else 0)
    elif max_val == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
        
    h /= 6
    return h, s, l

def get_basic_color_name(r, g, b):
    # Simple color binning
    if max(r, g, b) - min(r, g, b) < 30:
        brightness = (r + g + b) / 3
        if brightness < 64:
            return 'black'
        elif brightness < 128:
            return 'gray'
        else:
            return 'white'
    
    if r > max(g, b) + 30:
        return 'red'
    elif g > max(r, b) + 30:
        return 'green'
    elif b > max(r, g) + 30:
        return 'blue'
    elif r > 200 and g > 200 and b < 100:
        return 'yellow'
    elif r > 200 and g > 100 and b < 100:
        return 'orange'
    else:
        return 'mixed'

def analyze_image_colors(image):
    try:
        logger.info("Starting fast color analysis")
        
        # Convert to RGBA if not already
        if not isinstance(image, Image.Image):
            logger.error("Input must be a PIL Image")
            return None
            
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Convert to numpy array and remove transparent pixels
        pixels = np.array(image)
        mask = pixels[:, :, 3] > 128  # Alpha channel threshold
        rgb_pixels = pixels[mask][:, :3]
        
        if len(rgb_pixels) == 0:
            logger.error("No visible pixels found")
            return None
            
        # Reduce color space
        rgb_pixels = (rgb_pixels // 32) * 32
        
        # Get unique colors and their counts
        unique_colors, counts = np.unique(rgb_pixels, axis=0, return_counts=True)
        total_pixels = len(rgb_pixels)
        
        # Sort by frequency
        indices = np.argsort(-counts)
        sorted_colors = unique_colors[indices]
        sorted_counts = counts[indices]
        
        # Get top colors that make up at least 5% of the image
        color_frequencies = []
        cumulative_percent = 0
        
        for color, count in zip(sorted_colors, sorted_counts):
            percentage = (count / total_pixels) * 100
            if percentage < 5:
                continue
                
            r, g, b = map(int, color)
            color_name = get_basic_color_name(r, g, b)
            
            color_frequencies.append({
                'rgb': (r, g, b),
                'count': int(count),
                'percentage': percentage,
                'color_name': color_name
            })
            
            cumulative_percent += percentage
            if cumulative_percent > 90 or len(color_frequencies) >= 5:
                break
        
        if not color_frequencies:
            logger.error("No significant colors found")
            return None
            
        # Get dominant color
        dominant_color = color_frequencies[0]
        h, s, l = rgb_to_hsl(*dominant_color['rgb'])
        
        result = {
            'dominant_color': dominant_color['rgb'],
            'dominant_color_name': dominant_color['color_name'],
            'dominant_percentage': dominant_color['percentage'],
            'other_colors': color_frequencies[1:],
            'hue': h * 360,
            'saturation': s * 100,
            'lightness': l * 100
        }
        
        logger.info("Color analysis completed")
        return result 
        
    except Exception as e:
        logger.error(f"Error in analyze_image_colors: {str(e)}\nStack trace: {traceback.format_exc()}")
        return None