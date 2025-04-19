# apps\subscription_module\utils.py
import random
def get_random_color(exclude_h=None, exclude_range=0.1):
    while True:
        h = random.random()  # Random hue between 0 and 1
        # Check if this hue is too close to the excluded hue
        if exclude_h is not None:
            diff = min(abs(h - exclude_h), abs(h - (exclude_h + 1)), abs(h - (exclude_h - 1)))
            if diff < exclude_range:
                continue
        s = random.uniform(0.4, 1.0)  # Random saturation between 0.4 and 1
        v = random.uniform(0.4, 1.0)   # Random value between 0.4 and 1
        return h, s, v

def complementary(h, s, v):
    base_color = (h, s, v)
    comp_h = get_random_color(exclude_h=h)[0]
    return [base_color, (comp_h, s, v)]

def triadic(h, s, v):
    base_color = (h, s, v)
    colors = [base_color]
    used_hues = {h}
    
    for _ in range(2):
        new_h, new_s, new_v = get_random_color(exclude_h=h)
        while any(abs(new_h - used_h) < 0.1 for used_h in used_hues):
            new_h, new_s, new_v = get_random_color(exclude_h=h)
        colors.append((new_h, s, v))
        used_hues.add(new_h)
    
    return colors

def analogous(h, s, v, num_colors):
    base_color = (h, s, v)
    colors = [base_color]
    used_hues = {h}
    
    for _ in range(num_colors):
        new_h, new_s, new_v = get_random_color(exclude_h=h)
        while any(abs(new_h - used_h) < 0.1 for used_h in used_hues):
            new_h, new_s, new_v = get_random_color(exclude_h=h)
        colors.append((new_h, s, v))
        used_hues.add(new_h)
    
    return colors

def square_harmony(h, s, v):
    base_color = (h, s, v)
    colors = [base_color]
    used_hues = {h}
    
    for _ in range(3):
        new_h, new_s, new_v = get_random_color(exclude_h=h)
        while any(abs(new_h - used_h) < 0.1 for used_h in used_hues):
            new_h, new_s, new_v = get_random_color(exclude_h=h)
        colors.append((new_h, s, v))
        used_hues.add(new_h)
    
    return colors

def adjust_colors_by_type(colors, palette_type):
    adjusted_colors = []
    for h, s, v in colors:
        if palette_type == 'SS':  # Spring/Summer
            s = min(s + 0.15, 1.0)
            v = min(v + 0.15, 1.0)
        elif palette_type == 'AW':  # Autumn/Winter
            s = max(s - 0.15, 0.0)
            v = max(v - 0.15, 0.0)
        elif palette_type == 'TR':  # Trending
            s = min(s + 0.05, 1.0)
            v = min(v + 0.05, 1.0)
        adjusted_colors.append((h, s, v))
    return adjusted_colors

import colorsys
from django import forms
from .models import Palette, Color as ColorModel
import webcolors
from scipy.spatial import KDTree
import numpy as np

def get_color_name(rgb):
    r, g, b = rgb

    # Define color ranges and names
    def get_hue_name(h):
        if h < 15 or h >= 345:
            return "Red"
        elif 15 <= h < 45:
            return "Orange"
        elif 45 <= h < 75:
            return "Yellow"
        elif 75 <= h < 165:
            return "Green"
        elif 165 <= h < 195:
            return "Cyan"
        elif 195 <= h < 255:
            return "Blue"
        elif 255 <= h < 285:
            return "Purple"
        elif 285 <= h < 345:
            return "Pink"

    def get_shade_prefix(s, v):
        if v < 0.2:
            return "Dark"
        elif v > 0.8:
            return "Light"
        elif s < 0.2:
            return "Gray"
        elif s > 0.8:
            return "Vivid"
        return ""

    # Convert RGB to HSV
    r, g, b = r/255.0, g/255.0, b/255.0
    max_rgb = max(r, g, b)
    min_rgb = min(r, g, b)
    diff = max_rgb - min_rgb

    # Calculate Hue
    if max_rgb == min_rgb:
        h = 0
    elif max_rgb == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_rgb == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360

    # Calculate Saturation
    s = 0 if max_rgb == 0 else (diff / max_rgb)

    # Value
    v = max_rgb

    # Special cases for grayscale
    if s < 0.1:
        if v < 0.2:
            return "Black"
        elif v < 0.4:
            return "Dark Gray"
        elif v < 0.6:
            return "Gray"
        elif v < 0.8:
            return "Light Gray"
        else:
            return "White"

    # Get the base hue name
    hue_name = get_hue_name(h)
    
    # Get shade prefix
    shade_prefix = get_shade_prefix(s, v)
    
    # Combine prefix and hue name
    if shade_prefix:
        return f"{shade_prefix} {hue_name}"
    return hue_name

class AutoPaletteGenerationForm(forms.Form):
    base_color = forms.CharField(max_length=7, widget=forms.TextInput(attrs={'type': 'color'}))
    num_colors = forms.IntegerField(min_value=2, max_value=10)
    palette_type = forms.ChoiceField(choices=Palette.TYPE_CHOICES)
    auto_name = forms.BooleanField(required=False, initial=True)
    custom_name = forms.CharField(max_length=100, required=False)

    def clean(self):
        cleaned_data = super().clean()
        auto_name = cleaned_data.get('auto_name')
        custom_name = cleaned_data.get('custom_name')
        
        if not auto_name and not custom_name:
            raise forms.ValidationError("Either enable auto-naming or provide a custom name")
        return cleaned_data

    def generate_palette(self, user):
        base_color = self.cleaned_data['base_color']
        num_colors = self.cleaned_data['num_colors']
        palette_type = self.cleaned_data['palette_type']
        auto_name = self.cleaned_data['auto_name']
        custom_name = self.cleaned_data['custom_name']

        # Convert hex to RGB
        r, g, b = tuple(int(base_color[i:i+2], 16) for i in (1, 3, 5))
        
        # Get color name for auto-naming
        base_color_name = get_color_name((r, g, b))
        
        # Use custom name if provided, otherwise generate auto name
        if custom_name:
            palette_name = custom_name
        else:
            palette_name = f"{base_color_name.title()}"

        # Convert RGB to HSV
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        # Create new palette
        palette = Palette.objects.create(
            name=palette_name,
            creator=user,
            num_colors=num_colors,
            base_color=base_color,
            base_color_r=r,
            base_color_g=g,
            base_color_b=b,
            type=palette_type
        )

        # Create the first color (base color)
        ColorModel.objects.create(
            palette=palette,
            red=r,
            green=g,
            blue=b,
            name=base_color_name
        )

        # Generate remaining colors
        remaining_colors = num_colors - 1  # Subtract 1 for the base color
        harmony_colors = []
        
        for i in range(remaining_colors):
            # Generate new HSV color
            new_h = (h + (i + 1) * (1.0 / num_colors) + random.uniform(-0.1, 0.1)) % 1.0
            new_s = max(0.3, min(1.0, s + random.uniform(-0.2, 0.2)))
            new_v = max(0.3, min(1.0, v + random.uniform(-0.2, 0.2)))
            harmony_colors.append((new_h, new_s, new_v))

        # Adjust colors based on palette type
        adjusted_colors = adjust_colors_by_type(harmony_colors, palette_type)

        # Create remaining colors
        for hsv_color in adjusted_colors:
            h, s, v = hsv_color
            # Ensure minimum values
            s = max(0.3, min(1.0, s))
            v = max(0.3, min(1.0, v))
            
            # Convert HSV to RGB
            rgb = colorsys.hsv_to_rgb(h, s, v)
            r, g, b = [max(1, min(255, int(x * 255))) for x in rgb]  # Ensure values between 1 and 255
            
            color_name = get_color_name((r, g, b))
            
            # Create color object with validation
            try:
                ColorModel.objects.create(
                    palette=palette,
                    red=r,
                    green=g,
                    blue=b,
                    name=color_name
                )
            except Exception as e:
                print(f"Error creating color: HSV({h}, {s}, {v}), RGB({r}, {g}, {b})")
                raise e

        return palette



def ensure_contrast(color, background_luminance):
    h, s, v = color
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    color_luminance = (0.299 * r + 0.587 * g + 0.114 * b)
    
    if abs(color_luminance - background_luminance) < 0.4:
        if background_luminance > 0.5:
            v = max(v - 0.4, 0.0)
        else:
            v = min(v + 0.4, 1.0)
    
    return h, s, v