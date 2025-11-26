"""
Standalone Palette-Based Photo Recoloring
==========================================

A completely standalone script with all dependencies embedded.
No external imports needed except PIL, numpy, and standard library.

Usage as module:
    from palette_recolor_standalone import PaletteRecolor
    
    recolorer = PaletteRecolor()
    result = recolorer.recolor_image(
        image_path='input.jpg',
        original_colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)],
        new_colors=[(0, 255, 255), (255, 0, 255), (255, 255, 0)],
        output_path='output.jpg'
    )

Usage from command line:
    python palette_recolor_standalone.py --image input.jpg --original "255,0,0;0,255,0" --new "0,255,255;255,0,255"
"""

import random
import itertools
import math
import time
import argparse
import os
from PIL import Image, ImageCms
import numpy
from multiprocessing import Pool, cpu_count


# ============================================================================
# UTILITY FUNCTIONS (from util.py)
# ============================================================================

def rgb2lab(image):
    """Convert RGB image to LAB color space."""
    RGB_p = ImageCms.createProfile('sRGB')
    LAB_p = ImageCms.createProfile('LAB')
    return ImageCms.profileToProfile(image, RGB_p, LAB_p, outputMode='LAB')


def lab2rgb(image):
    """Convert LAB image to RGB color space."""
    RGB_p = ImageCms.createProfile('sRGB')
    LAB_p = ImageCms.createProfile('LAB')
    return ImageCms.profileToProfile(image, LAB_p, RGB_p, outputMode='RGB')


def LABtoXYZ(LAB):
    """Convert LAB to XYZ color space."""
    def f(n):
        return n**3 if n > 6/29 else 3 * ((6/29)**2) * (n - 4/29)

    assert(ValidLAB(LAB))

    L, a, b = LAB
    X = 95.047 * f((L+16)/116 + a/500)
    Y = 100.000 * f((L+16)/116)
    Z = 108.883 * f((L+16)/116  - b/200)
    return (X, Y, Z)


def XYZtoRGB(XYZ):
    """Convert XYZ to RGB color space."""
    def f(n):
        return n*12.92 if n <= 0.0031308 else (n**(1/2.4)) * 1.055 - 0.055

    X, Y, Z = [x/100 for x in XYZ]
    R = f(3.2406*X + -1.5372*Y + -0.4986*Z) * 255
    G = f(-0.9689*X + 1.8758*Y + 0.0415*Z) * 255
    B = f(0.0557*X + -0.2040*Y + 1.0570*Z) * 255
    return (R, G, B)


def LABtoRGB(LAB):
    """Convert LAB to RGB color space."""
    return XYZtoRGB(LABtoXYZ(LAB))


def RGBtoXYZ(RGB):
    """Convert RGB to XYZ color space."""
    def f(n):
        return n/12.92 if n <= 0.04045 else ((n+0.055)/1.055)**2.4

    assert(ValidRGB(RGB))

    R, G, B = [f(x/255) for x in RGB]
    X = (0.4124*R + 0.3576*G + 0.1805*B) * 100
    Y = (0.2126*R + 0.7152*G + 0.0722*B) * 100
    Z = (0.0193*R + 0.1192*G + 0.9505*B) * 100
    return (X, Y, Z)


def XYZtoLAB(XYZ):
    """Convert XYZ to LAB color space."""
    def f(n):
        return n**(1/3) if n > (6/29)**3 else (n / (3*((6/29)**2))) + (4/29)

    X, Y, Z = XYZ
    X /= 95.047
    Y /= 100.000
    Z /= 108.883

    L = 116*f(Y) - 16
    a = 500 * (f(X) - f(Y))
    b = 200 * (f(Y) - f(Z))
    return (L, a, b)


def RGBtoLAB(RGB):
    """Convert RGB to LAB color space."""
    return XYZtoLAB(RGBtoXYZ(RGB))


def ValidRGB(RGB):
    """Check if RGB values are valid."""
    return False not in [0 <= x <= 255 for x in RGB]


def ValidLAB(LAB):
    """Check if LAB values are valid."""
    L, a, b = LAB
    return 0 <= L <= 100 and -128 <= a <= 127 and -128 <= b <= 127


def RegularLAB(LAB):
    """Convert byte LAB to regular LAB."""
    return (LAB[0] / 255 * 100, LAB[1] - 128, LAB[2] - 128)


def ByteLAB(LAB):
    """Convert regular LAB to byte LAB."""
    return (int(LAB[0] / 100 * 255), int(LAB[1] + 128), int(LAB[2] + 128))


def RegularRGB(RGB):
    """Clamp RGB values to valid range."""
    return tuple([int(max(0, min(x, 255))) for x in RGB])


def distance(color_a, color_b):
    """Calculate Euclidean distance between two colors."""
    return (sum([(a-b)**2 for a, b in zip(color_a, color_b)]))**0.5


# ============================================================================
# PALETTE EXTRACTION (from palette.py)
# ============================================================================

def k_means(bins, means, k, maxiter=1000, black=True):
    """K-means clustering for color palette extraction."""
    record = {}
    for color in bins.keys():
        record[color] = -1

    if black:
        means.append((0, 128, 128))

    for _ in range(maxiter):
        done = True
        cluster_sum = [[0, 0, 0] for _ in range(len(means))]
        cluster_size = [0 for _ in range(len(means))]

        # Assign
        for color, count in bins.items():
            dists = [distance(color, mean) for mean in means]
            cluster = dists.index(min(dists))

            if record[color] != cluster:
                record[color] = cluster
                done = False

            for i in range(3):
                cluster_sum[cluster][i] += color[i] * count
            cluster_size[cluster] += count

        # Update
        for i in range(k):
            if cluster_size[i] > 0:
                means[i] = tuple([cluster_sum[i][j] / cluster_size[i] for j in range(3)])

        if done:
            break

    return means[:k]


def simple_bins(bins, size=16):
    """Simplify color bins for faster processing."""
    level = 256//size
    temp = {}
    for x in itertools.product(range(size), repeat=3):
        temp[x] = {'size': 0, 'sum': [0, 0, 0]}

    for color, count in bins.items():
        index = tuple([c//level for c in color])
        for i in range(3):
            temp[index]['sum'][i] += color[i] * count
        temp[index]['size'] += count

    result = {}
    for color in temp.values():
        if color['size'] != 0:
            result[tuple([color['sum'][j] / color['size'] for j in range(3)])] = color['size']

    return result


def init_means(bins, k):
    """Initialize k-means with smart selection."""
    def attenuation(color, target):
        return 1 - math.exp(((distance(color, target)/80)**2) * -1)

    colors = []
    for color, count in bins.items():
        colors.append([count, color])
    colors.sort(reverse=True)

    result = []
    for _ in range(k):
        for color in colors:
            if color[1] not in result:
                result.append(color[1])
                break

        for i in range(len(colors)):
            colors[i][0] *= attenuation(colors[i][1], result[-1])

        colors.sort(reverse=True)

    return result


def build_palette(image, k=5, random_init=False, black=True):
    """Extract color palette from image using k-means clustering."""
    colors = image.getcolors(image.width * image.height)
    print('colors num:', len(colors))

    bins = {}
    for count, pixel in colors:
        bins[pixel] = count
    bins = simple_bins(bins)

    if random_init: 
        init = random.sample(list(bins), k)
    else:
        init = init_means(bins, k)

    means = k_means(bins, init, k, black=black)
    means.sort(reverse=True)
    colors = [tuple([int(x) for x in color]) for color in means]
    print('Build palette', colors)
    return colors


# ============================================================================
# COLOR TRANSFER (from transfer.py)
# ============================================================================

class Vec3:
    """3D vector for color operations."""
    def __init__(self, data):
        self.data = data

    def __add__(self, other):
        return Vec3([x + y for x, y in zip(self.data, other.data)])

    def __sub__(self, other):
        return Vec3([x - y for x, y in zip(self.data, other.data)])

    def __mul__(self, other):
        return Vec3([x * other for x in self.data])

    def __truediv__(self, other):
        return Vec3([x / other for x in self.data])

    def len(self):
        return (sum([x**2 for x in self.data]))**0.5


def luminance_transfer(color, original_p, modified_p):
    """Transfer luminance from original to modified palette."""
    def interpolation(xa, xb, ya, yb, z):
        return (ya*(xb-z) + yb*(z-xa)) / (xb - xa)

    l = color[0]
    original_l = [100] + [l for l, a, b in original_p] + [0]
    modified_l = [100] + [l for l, a, b in modified_p] + [0]
    
    if l > 100:
        return 100
    elif l <= 0:
        return 0
    else:
        for i in range(len(original_l)):
            if original_l[i] == l:
                return modified_l[i]
            elif original_l[i] > l > original_l[i+1]:
                return interpolation(original_l[i], original_l[i+1], modified_l[i], modified_l[i+1], l)


def single_color_transfer(color, original_c, modified_c):
    """Transfer single color with boundary detection."""
    def get_boundary(origin, direction, k_min, k_max, iters=20):
        start = origin + direction * k_min
        end = origin + direction * k_max
        for _ in range(iters):
            mid = (start + end) / 2
            if ValidLAB(mid.data) and ValidRGB(LABtoRGB(mid.data)):
                start = mid
            else:
                end = mid
        return (start + end) / 2

    color = Vec3(color)
    original_c = Vec3(original_c)
    modified_c = Vec3(modified_c)
    offset = modified_c - original_c

    c_boundary = get_boundary(original_c, offset, 1, 255)
    naive = (color + offset).data
    if ValidLAB(naive) and ValidRGB(LABtoRGB(naive)):
        boundary = get_boundary(color, offset, 1, 255)
    else:
        boundary = get_boundary(modified_c, color - original_c, 0, 1)

    if (boundary - color).len() == 0:
        result = color
    elif (boundary - color).len() < (c_boundary - original_c).len():
        result = color + (boundary - color) * (offset.len() / (c_boundary - original_c).len())
    else:
        result = color + (boundary - color) * (offset.len() / (boundary - color).len())

    return result


def calc_weights(color, original_p):
    """Calculate Gaussian weights for color transfer."""
    def mean_distance(original_p):
        dists = []
        for a, b in itertools.combinations(original_p, 2):
            dists.append(distance(a, b))
        return sum(dists) / len(dists)

    def gaussian(r, md):
        return math.exp(((r/md)**2) * -0.5)

    md = mean_distance(original_p)

    matrix = []
    for i in range(len(original_p)):
        temp = []
        for j in range(len(original_p)):
            temp.append(gaussian(distance(original_p[j], original_p[i]), md))
        matrix.append(temp)
    phi = numpy.array(matrix)
    lamb = numpy.linalg.inv(phi)

    weights = [0 for _ in range(len(original_p))]
    for i in range(len(original_p)):
        for j in range(len(original_p)):
            weights[i] += lamb[i][j] * gaussian(distance(color, original_p[j]), md)

    weights = [w if w >=0 else 0 for w in weights]
    w_sum = sum(weights)
    weights = [w/w_sum for w in weights]

    return weights


def multiple_color_transfer(color, original_p, modified_p):
    """Transfer color using multiple palette colors with weighting."""
    color_st = []
    for i in range(len(original_p)):
        color_st.append(single_color_transfer(color, original_p[i], modified_p[i]))

    weights = calc_weights(color, original_p)

    color_mt = Vec3([0, 0, 0])
    for i in range(len(original_p)):
        color_mt = color_mt + color_st[i] * weights[i]

    return color_mt.data


def RGB_sample_color(size=16):
    """Generate RGB sample colors for interpolation."""
    assert(size >= 2)
    levels = [i * (255/(size-1)) for i in range(size)]
    colors = []
    for r, g, b in itertools.product(levels, repeat=3):
        colors.append((r, g, b))
    return colors


def nearest_color(target, level, levels):
    """Find nearest color levels for interpolation."""
    nearest_level = []
    for ch in target:
        index = ch / level
        nearest_level.append((levels[math.floor(index)], levels[math.ceil(index)]))
    return nearest_level


def trilinear_interpolation(target, corners, sample_color_map):
    """Perform trilinear interpolation for smooth color transitions."""
    RGBr = []
    for i in range(3):
        temp = (target[i] - corners[i][0]) / (corners[i][1] - corners[i][0]) if corners[i][0] != corners[i][1] else 0
        RGBr.append((1 - temp, temp))

    rates = []
    for Rr, Gr, Br in itertools.product(*RGBr):
        rates.append(Rr * Gr * Br)

    result = [0, 0, 0]
    for color, rate in zip(itertools.product(*corners), rates):
        sc = sample_color_map[color]
        for i in range(3):
            result[i] += sc[i] * rate

    return result


def luminance_transfer_mt(args):
    """Multiprocessing wrapper for luminance transfer."""
    return luminance_transfer(*args)


def multiple_color_transfer_mt(args):
    """Multiprocessing wrapper for color transfer."""
    return multiple_color_transfer(*args)


def trilinear_interpolation_mt(args):
    """Multiprocessing wrapper for interpolation."""
    return trilinear_interpolation(*args)


def rgb_to_hsv(rgb):
    """Convert RGB to HSV color space."""
    r, g, b = [x / 255.0 for x in rgb]
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    diff = max_c - min_c
    
    if max_c == min_c:
        h = 0
    elif max_c == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_c == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    
    s = 0 if max_c == 0 else (diff / max_c)
    v = max_c
    
    return (h, s, v)


def get_hue_angles(palette_rgb):
    """Get hue angles from RGB palette."""
    hues = []
    for color in palette_rgb:
        h, s, v = rgb_to_hsv(color)
        # Only consider colors with sufficient saturation
        if s > 0.1:  # Ignore near-grayscale colors
            hues.append(h)
    return hues


def angle_distance(a1, a2):
    """Calculate shortest distance between two angles (0-360)."""
    diff = abs(a1 - a2)
    return min(diff, 360 - diff)


def detect_color_harmony(palette_rgb):
    """
    Detect the type of color harmony in a palette.
    
    Returns:
        str: One of 'monochromatic', 'analogous', 'complementary', 
             'split-complementary', 'triadic', 'tetradic', 'square', or 'custom'
    """
    if len(palette_rgb) <= 1:
        return 'monochromatic'
    
    hues = get_hue_angles(palette_rgb)
    
    if len(hues) == 0:
        # All grayscale
        return 'monochromatic'
    
    if len(hues) == 1:
        return 'monochromatic'
    
    # Sort hues for analysis
    hues_sorted = sorted(hues)
    
    # Check for monochromatic (all hues within 30 degrees)
    max_hue_diff = max(angle_distance(hues_sorted[i], hues_sorted[i+1]) 
                       for i in range(len(hues_sorted)-1))
    if max_hue_diff < 30:
        return 'monochromatic'
    
    # Check for analogous (hues within 60 degrees)
    hue_span = angle_distance(hues_sorted[0], hues_sorted[-1])
    if hue_span <= 60:
        return 'analogous'
    
    # Check for complementary (2 hues ~180 degrees apart)
    if len(hues) == 2:
        dist = angle_distance(hues[0], hues[1])
        if 150 <= dist <= 210:
            return 'complementary'
    
    # Check for split-complementary (3 hues: one + two ~150 degrees away)
    if len(hues) == 3:
        # Check if one hue is opposite to the other two
        for i in range(3):
            other_two = [hues[j] for j in range(3) if j != i]
            dist1 = angle_distance(hues[i], other_two[0])
            dist2 = angle_distance(hues[i], other_two[1])
            if 120 <= dist1 <= 180 and 120 <= dist2 <= 180:
                return 'split-complementary'
    
    # Check for triadic (3 hues ~120 degrees apart)
    if len(hues) == 3:
        dists = [angle_distance(hues_sorted[i], hues_sorted[(i+1)%3]) 
                 for i in range(3)]
        if all(90 <= d <= 150 for d in dists):
            return 'triadic'
    
    # Check for tetradic/square (4 hues)
    if len(hues) == 4:
        dists = [angle_distance(hues_sorted[i], hues_sorted[(i+1)%4]) 
                 for i in range(4)]
        avg_dist = sum(dists) / len(dists)
        
        # Square: ~90 degrees apart
        if 75 <= avg_dist <= 105:
            return 'square'
        # Tetradic: two pairs of complementary colors
        elif all(60 <= d <= 120 or 150 <= d <= 210 for d in dists):
            return 'tetradic'
    
    return 'custom'


def is_monochromatic_palette(palette_rgb, threshold=50):
    """
    Check if a palette is monochromatic (all colors have similar hue).
    
    Args:
        palette_rgb: List of RGB tuples
        threshold: Maximum color distance to consider monochromatic
    
    Returns:
        bool: True if palette is monochromatic
    """
    if len(palette_rgb) <= 1:
        return True
    
    # Check if all colors are grayscale
    all_gray = all(abs(r - g) < 10 and abs(g - b) < 10 and abs(r - b) < 10 
                   for r, g, b in palette_rgb)
    if all_gray:
        print("  → Detected as grayscale")
        return True
    
    # Check if all colors have similar hue (in LAB space, check a and b channels)
    lab_colors = [RGBtoLAB(color) for color in palette_rgb]
    avg_a = sum(a for _, a, b in lab_colors) / len(lab_colors)
    avg_b = sum(b for _, a, b in lab_colors) / len(lab_colors)
    
    print(f"  → Average hue in LAB (a, b): ({avg_a:.1f}, {avg_b:.1f})")
    
    # Check if all colors are close to the average hue
    max_distance = 0
    for _, a, b in lab_colors:
        dist = distance((a, b), (avg_a, avg_b))
        max_distance = max(max_distance, dist)
    
    print(f"  → Max hue distance from average: {max_distance:.1f} (threshold: {threshold})")
    
    if max_distance > threshold:
        return False
    
    print(f"  → Detected as monochromatic (single hue)")
    return True


def simple_monochrome_transfer(color, original_p, modified_p):
    """
    Simple color transfer for monochromatic palettes.
    Maps based on luminance only, applying the target hue uniformly.
    
    Args:
        color: Color in LAB space (L, a, b)
        original_p: Original palette in LAB (regular format)
        modified_p: Modified palette in LAB (regular format)
    
    Returns:
        Transferred color in LAB space
    """
    # Get the luminance of the input color
    L = color[0]
    
    # Find the average hue from the modified palette
    avg_a = sum(a for _, a, b in modified_p) / len(modified_p)
    avg_b = sum(b for _, a, b in modified_p) / len(modified_p)
    
    # Find the closest luminance in original palette
    original_L = sorted([l for l, _, _ in original_p])
    modified_L = sorted([l for l, _, _ in modified_p])
    
    # Map luminance from original range to modified range
    if len(original_L) > 1:
        # Normalize L to 0-1 range based on original palette
        L_min_orig = min(original_L)
        L_max_orig = max(original_L)
        L_min_mod = min(modified_L)
        L_max_mod = max(modified_L)
        
        if L_max_orig > L_min_orig:
            L_normalized = (L - L_min_orig) / (L_max_orig - L_min_orig)
            L_normalized = max(0, min(1, L_normalized))  # Clamp to 0-1
            new_L = L_min_mod + L_normalized * (L_max_mod - L_min_mod)
        else:
            new_L = modified_L[0]
    else:
        new_L = modified_L[0]
    
    # Apply the average hue with the mapped luminance
    return (new_L, avg_a, avg_b)


def simple_harmony_transfer(color, original_p, modified_p, harmony_type):
    """
    Simplified color transfer for color harmony palettes.
    Uses a hybrid approach: preserves some color relationships but simplifies the transfer.
    
    Args:
        color: Color in LAB space (L, a, b)
        original_p: Original palette in LAB (regular format)
        modified_p: Modified palette in LAB (regular format)
        harmony_type: Type of color harmony
    
    Returns:
        Transferred color in LAB space
    """
    # For analogous and other harmonies, use a simplified version of the full algorithm
    # Find the closest color in the original palette
    min_dist = float('inf')
    closest_idx = 0
    
    for i, orig_color in enumerate(original_p):
        dist = distance(color, orig_color)
        if dist < min_dist:
            min_dist = dist
            closest_idx = i
    
    # Use the corresponding color from the modified palette as the base
    base_color = modified_p[closest_idx]
    
    # Calculate offset from the closest original color
    offset_L = color[0] - original_p[closest_idx][0]
    offset_a = color[1] - original_p[closest_idx][1]
    offset_b = color[2] - original_p[closest_idx][2]
    
    # Apply a dampened offset to preserve some variation
    # For harmonies, we want to preserve color relationships more than monochrome
    damping = 0.7 if harmony_type == 'analogous' else 0.5
    
    new_L = base_color[0] + offset_L * damping
    new_a = base_color[1] + offset_a * damping
    new_b = base_color[2] + offset_b * damping
    
    # Clamp to valid LAB ranges
    new_L = max(0, min(100, new_L))
    new_a = max(-128, min(127, new_a))
    new_b = max(-128, min(127, new_b))
    
    return (new_L, new_a, new_b)


def aggressive_color_transfer(color, original_p, modified_p):
    """
    Aggressive color transfer that fully replaces colors.
    Maps each pixel to the closest palette color with minimal blending.
    
    Args:
        color: Color in LAB space (L, a, b)
        original_p: Original palette in LAB (regular format)
        modified_p: Modified palette in LAB (regular format)
    
    Returns:
        Transferred color in LAB space
    """
    # Find the closest color in the original palette
    min_dist = float('inf')
    closest_idx = 0
    
    for i, orig_color in enumerate(original_p):
        dist = distance(color, orig_color)
        if dist < min_dist:
            min_dist = dist
            closest_idx = i
    
    # Get the corresponding color from the modified palette
    target_color = modified_p[closest_idx]
    
    # Calculate luminance offset to preserve some depth
    L_offset = color[0] - original_p[closest_idx][0]
    
    # Apply only luminance offset, but keep the target hue
    # This preserves brightness variations while fully replacing colors
    new_L = target_color[0] + L_offset * 0.8  # 80% luminance preservation
    new_a = target_color[1]  # Full hue replacement
    new_b = target_color[2]  # Full hue replacement
    
    # Clamp to valid LAB ranges
    new_L = max(0, min(100, new_L))
    
    return (new_L, new_a, new_b)


def image_transfer(image, original_p, modified_p, sample_level=16, luminance_flag=False, monochrome_mode=False, harmony_type=None, aggressive_mode=True):
    """
    Apply palette-based color transfer to entire image.
    
    Args:
        image: PIL Image in LAB color space
        original_p: Original palette in LAB
        modified_p: Modified palette in LAB
        sample_level: Resolution for color sampling
        luminance_flag: Whether to preserve luminance
        monochrome_mode: Force monochromatic transfer
        harmony_type: Type of color harmony (auto-detected if None)
        aggressive_mode: Use aggressive color replacement
    
    Returns:
        PIL Image in LAB color space
    """
    t = time.time()
    
    original_p = [RegularLAB(c) for c in original_p]
    modified_p = [RegularLAB(c) for c in modified_p]
    level = 255 / (sample_level - 1)
    levels = [i * (255/(sample_level-1)) for i in range(sample_level)]

    # Build sample color map
    print('Build sample color map')
    t2 = time.time()
    sample_color_map = {}
    sample_colors = RGB_sample_color(sample_level)

    args = []
    for color in sample_colors:
        args.append((RegularLAB(color), original_p, modified_p))

    # Use simplified transfer for monochrome and harmony types
    use_simplified = monochrome_mode or (harmony_type and harmony_type != 'custom') or aggressive_mode
    
    if monochrome_mode:
        # Use simple monochrome transfer for monochromatic palettes
        print('Using monochrome transfer mode')
        for i, color in enumerate(sample_colors):
            lab_result = simple_monochrome_transfer(RegularLAB(color), original_p, modified_p)
            sample_color_map[color] = ByteLAB(lab_result)
    elif aggressive_mode and harmony_type == 'custom':
        # Use aggressive transfer for custom palettes
        print('Using aggressive color replacement mode')
        for i, color in enumerate(sample_colors):
            lab_result = aggressive_color_transfer(RegularLAB(color), original_p, modified_p)
            sample_color_map[color] = ByteLAB(lab_result)
    elif harmony_type and harmony_type in ['analogous', 'complementary', 'split-complementary', 'triadic', 'tetradic', 'square']:
        # Use simplified harmony transfer
        print(f'Using simplified {harmony_type} transfer mode')
        for i, color in enumerate(sample_colors):
            lab_result = simple_harmony_transfer(RegularLAB(color), original_p, modified_p, harmony_type)
            sample_color_map[color] = ByteLAB(lab_result)
    elif luminance_flag:
        with Pool(cpu_count()-1) as pool:
            l = pool.map(luminance_transfer_mt, args)
            lab = pool.map(multiple_color_transfer_mt, args)

        for i in range(len(sample_colors)):
            sample_color_map[sample_colors[i]] = ByteLAB((l[i], *lab[i][-2:]))
    else:
        with Pool(cpu_count()-1) as pool:
            lab = pool.map(multiple_color_transfer_mt, args)

        for i in range(len(sample_colors)):
            sample_color_map[sample_colors[i]] = ByteLAB(lab[i])

    print('Build sample color map time', time.time() - t2)
    t2 = time.time()

    # Build color map
    print('Build color map')
    color_map = {}
    colors = image.getcolors(image.width * image.height)

    args = []
    for _, color in colors:
        nc = nearest_color(color, level, levels)
        args.append((color, nc, sample_color_map))
    with Pool(cpu_count()-1) as pool:
        inter_result = pool.map(trilinear_interpolation_mt, args)

    for i in range(len(colors)):
        color_map[colors[i][1]] = tuple([int(x) for x in inter_result[i]])
    print('Build color map time', time.time() - t2)
    t2 = time.time()

    # Transfer image
    print('Transfer image')
    result = Image.new('LAB', image.size)
    result_pixels = result.load()
    image_pixels = image.load()
    for i in range(image.width):
        for j in range(image.height):
            result_pixels[i, j] = color_map[image_pixels[i, j]]
    print('Transfer image time', time.time() - t2)

    print('Total time', time.time() - t)
    return result


# ============================================================================
# MAIN RECOLORING CLASS
# ============================================================================

class PaletteRecolor:
    """
    Palette-based photo recoloring using the algorithm from:
    "Palette-based Photo Recoloring" by Chang et al.
    """
    
    def __init__(self, sample_level=16, luminance_flag=True, monochrome_mode=False, aggressive_mode=True):
        """
        Initialize the recolorer.
        
        Args:
            sample_level (int): Resolution for color sampling (default: 16)
            luminance_flag (bool): Whether to preserve luminance (default: True)
            monochrome_mode (bool): Force monochromatic output (default: False)
            aggressive_mode (bool): Use aggressive color replacement (default: True)
        """
        self.sample_level = sample_level
        self.luminance_flag = luminance_flag
        self.monochrome_mode = monochrome_mode
        self.aggressive_mode = aggressive_mode
    
    def recolor_image(self, image_path, original_colors, new_colors, output_path=None):
        """
        Recolor an image using palette-based color transfer.
        
        Args:
            image_path (str): Path to input image
            original_colors (list): List of RGB tuples representing original palette
                                   e.g., [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            new_colors (list): List of RGB tuples representing new palette
                              Must be same length as original_colors
            output_path (str, optional): Path to save output image. If None, returns PIL Image
        
        Returns:
            PIL.Image: Recolored image (if output_path is None)
            str: Path to saved image (if output_path is provided)
        """
        if len(original_colors) != len(new_colors):
            raise ValueError("original_colors and new_colors must have the same length")
        
        if not original_colors:
            raise ValueError("Color palettes cannot be empty")
        
        print(f"Loading image: {image_path}")
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        print(f"Image size: {image.size}")
        
        print("Converting to LAB color space...")
        lab_image = rgb2lab(image)
        
        print("Converting color palettes to LAB...")
        original_palette_lab = self._rgb_palette_to_lab(original_colors)
        new_palette_lab = self._rgb_palette_to_lab(new_colors)
        
        print(f"Original palette (RGB): {original_colors}")
        print(f"New palette (RGB): {new_colors}")
        print(f"Original palette (LAB): {original_palette_lab}")
        print(f"New palette (LAB): {new_palette_lab}")
        
        # Detect color harmony type
        harmony_type = detect_color_harmony(new_colors)
        print(f"Detected color harmony: {harmony_type}")
        
        # Auto-detect monochromatic palette (legacy check)
        is_mono = is_monochromatic_palette(new_colors)
        use_monochrome = self.monochrome_mode or (harmony_type == 'monochromatic')
        
        if use_monochrome:
            print("✓ Using monochrome transfer mode")
        elif harmony_type != 'custom':
            print(f"✓ Using optimized {harmony_type} transfer mode")
        elif self.aggressive_mode:
            print("✓ Using aggressive color replacement mode")
        else:
            print("✓ Using standard multi-color transfer mode")
        
        print("Applying palette-based color transfer...")
        result_lab = image_transfer(
            lab_image,
            original_palette_lab,
            new_palette_lab,
            sample_level=self.sample_level,
            luminance_flag=self.luminance_flag,
            monochrome_mode=use_monochrome,
            harmony_type=harmony_type if not use_monochrome else None,
            aggressive_mode=self.aggressive_mode
        )
        
        print("Converting back to RGB...")
        result_rgb = lab2rgb(result_lab)
        
        if output_path:
            print(f"Saving result to: {output_path}")
            result_rgb.save(output_path)
            print("Done!")
            return output_path
        else:
            print("Done!")
            return result_rgb
    
    def recolor_image_auto_extract(self, image_path, new_colors, output_path=None, num_colors=None):
        """
        Recolor an image by automatically extracting the original palette.
        
        Args:
            image_path (str): Path to input image
            new_colors (list): List of RGB tuples representing new palette
            output_path (str, optional): Path to save output image
            num_colors (int, optional): Number of colors to extract. If None, uses len(new_colors)
        
        Returns:
            PIL.Image or str: Recolored image or path to saved image
        """
        print(f"Loading image: {image_path}")
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        lab_image = rgb2lab(image)
        
        if num_colors is None:
            num_colors = len(new_colors)
        
        print(f"Extracting {num_colors} colors from image...")
        original_palette_lab = build_palette(lab_image, k=num_colors, black=False)
        
        new_palette_lab = self._rgb_palette_to_lab(new_colors)
        
        if len(original_palette_lab) != len(new_palette_lab):
            print(f"Warning: Extracted {len(original_palette_lab)} colors but got {len(new_palette_lab)} new colors")
            min_len = min(len(original_palette_lab), len(new_palette_lab))
            original_palette_lab = original_palette_lab[:min_len]
            new_palette_lab = new_palette_lab[:min_len]
        
        print(f"Original palette (RGB): {[tuple(int(c) for c in color) for color in original_colors]}")
        print(f"New palette (RGB): {[tuple(int(c) for c in color) for color in new_colors]}")
        print(f"Original palette (LAB): {original_palette_lab}")
        print(f"New palette (LAB): {new_palette_lab}")
        
        # Detect color harmony type
        harmony_type = detect_color_harmony(new_colors)
        print(f"Detected color harmony: {harmony_type}")
        
        # Auto-detect monochromatic palette (legacy check)
        is_mono = is_monochromatic_palette(new_colors)
        use_monochrome = self.monochrome_mode or (harmony_type == 'monochromatic')
        
        if use_monochrome:
            print("✓ Using monochrome transfer mode")
        elif harmony_type != 'custom':
            print(f"✓ Using optimized {harmony_type} transfer mode")
        elif self.aggressive_mode:
            print("✓ Using aggressive color replacement mode")
        else:
            print("✓ Using standard multi-color transfer mode")
        
        print("Applying palette-based color transfer...")
        result_lab = image_transfer(
            lab_image,
            original_palette_lab,
            new_palette_lab,
            sample_level=self.sample_level,
            luminance_flag=self.luminance_flag,
            monochrome_mode=use_monochrome,
            harmony_type=harmony_type if not use_monochrome else None,
            aggressive_mode=self.aggressive_mode
        )
        
        print("Converting back to RGB...")
        result_rgb = lab2rgb(result_lab)
        
        if output_path:
            print(f"Saving result to: {output_path}")
            result_rgb.save(output_path)
            print("Done!")
            return output_path
        else:
            print("Done!")
            return result_rgb
    
    def extract_palette(self, image_path, num_colors=8):
        """
        Extract dominant colors from an image.
        
        Args:
            image_path (str): Path to input image
            num_colors (int): Number of colors to extract (default: 8)
        
        Returns:
            list: List of RGB tuples representing the extracted palette
        """
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        lab_image = rgb2lab(image)
        
        print(f"Extracting {num_colors} colors from image...")
        palette_lab = build_palette(lab_image, k=num_colors, black=False)
        
        palette_rgb = []
        for color_lab in palette_lab:
            rgb_img = Image.new('LAB', (1, 1), tuple([int(c) for c in color_lab]))
            rgb_converted = lab2rgb(rgb_img)
            rgb_color = rgb_converted.getpixel((0, 0))
            palette_rgb.append(rgb_color)
        
        print(f"Extracted palette (RGB): {palette_rgb}")
        return palette_rgb
    
    def _rgb_palette_to_lab(self, rgb_palette):
        """Convert RGB palette to LAB color space."""
        lab_palette = []
        for color in rgb_palette:
            if len(color) != 3:
                raise ValueError(f"Invalid color format: {color}. Expected (R, G, B)")
            
            rgb_img = Image.new('RGB', (1, 1), tuple([int(c) for c in color]))
            lab_img = rgb2lab(rgb_img)
            lab_color = lab_img.getpixel((0, 0))
            lab_palette.append(lab_color)
        
        return lab_palette


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def parse_color_string(color_str):
    """
    Parse color string to list of RGB tuples.
    Format: "R,G,B;R,G,B;R,G,B"
    """
    colors = []
    for color_part in color_str.split(';'):
        rgb = tuple(map(int, color_part.split(',')))
        if len(rgb) != 3:
            raise ValueError(f"Invalid color format: {color_part}")
        colors.append(rgb)
    return colors


def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(
        description='Palette-based photo recoloring',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Recolor with specific palettes
  python palette_recolor_standalone.py --image input.jpg --original "255,0,0;0,255,0;0,0,255" --new "0,255,255;255,0,255;255,255,0" --output result.jpg
  
  # Auto-extract original palette
  python palette_recolor_standalone.py --image input.jpg --new "100,200,200;200,100,200;200,200,100" --output result.jpg --auto
  
  # Extract palette only
  python palette_recolor_standalone.py --image input.jpg --extract 8
        """
    )
    
    parser.add_argument('--image', required=True, help='Input image path')
    parser.add_argument('--original', help='Original color palette (format: "R,G,B;R,G,B;...")')
    parser.add_argument('--new', help='New color palette (format: "R,G,B;R,G,B;...")')
    parser.add_argument('--output', help='Output image path (default: input_recolored.jpg)')
    parser.add_argument('--auto', action='store_true', help='Auto-extract original palette')
    parser.add_argument('--extract', type=int, help='Extract N colors and exit')
    parser.add_argument('--sample-level', type=int, default=16, help='Sample level (default: 16)')
    parser.add_argument('--no-luminance', action='store_true', help='Disable luminance preservation')
    parser.add_argument('--monochrome', action='store_true', help='Force monochromatic transfer mode')
    parser.add_argument('--no-aggressive', action='store_true', help='Disable aggressive color replacement (use conservative blending)')
    
    args = parser.parse_args()
    
    recolorer = PaletteRecolor(
        sample_level=args.sample_level,
        luminance_flag=not args.no_luminance,
        monochrome_mode=args.monochrome,
        aggressive_mode=not args.no_aggressive
    )
    
    if args.extract:
        palette = recolorer.extract_palette(args.image, num_colors=args.extract)
        print("\nExtracted Palette (RGB):")
        for i, color in enumerate(palette):
            print(f"  Color {i+1}: {color}")
        return
    
    if not args.new:
        parser.error("--new is required for recoloring")
    
    new_colors = parse_color_string(args.new)
    
    if not args.output:
        base, ext = os.path.splitext(args.image)
        args.output = f"{base}_recolored{ext}"
    
    if args.auto:
        recolorer.recolor_image_auto_extract(
            args.image,
            new_colors,
            args.output
        )
    else:
        if not args.original:
            parser.error("--original is required (or use --auto)")
        
        original_colors = parse_color_string(args.original)
        recolorer.recolor_image(
            args.image,
            original_colors,
            new_colors,
            args.output
        )


if __name__ == '__main__':
    main()
