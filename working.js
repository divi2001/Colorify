async applyMultipleColorMappings(imageData, colorMappings) {
    console.log("Starting multiple color mappings with improved algorithm");
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            console.time('colorMapping');
            const canvasElement = document.createElement('canvas');
            const ctx = canvasElement.getContext('2d');
            canvasElement.width = img.width;
            canvasElement.height = img.height;

            ctx.drawImage(img, 0, 0);
            const imageDataObj = ctx.getImageData(0, 0, img.width, img.height);
            const data = imageDataObj.data;

            // Color conversion utilities
            function rgbToLab(r, g, b) {
                r /= 255; g /= 255; b /= 255;

                r = r > 0.04045 ? Math.pow((r + 0.055) / 1.055, 2.4) : r / 12.92;
                g = g > 0.04045 ? Math.pow((g + 0.055) / 1.055, 2.4) : g / 12.92;
                b = b > 0.04045 ? Math.pow((b + 0.055) / 1.055, 2.4) : b / 12.92;

                let x = (r * 0.4124564 + g * 0.3575761 + b * 0.1804375) * 100;
                let y = (r * 0.2126729 + g * 0.7151522 + b * 0.0721750) * 100;
                let z = (r * 0.0193339 + g * 0.1191920 + b * 0.9503041) * 100;

                x /= 95.047; y /= 100; z /= 108.883;

                x = x > 0.008856 ? Math.pow(x, 1/3) : (7.787 * x) + 16/116;
                y = y > 0.008856 ? Math.pow(y, 1/3) : (7.787 * y) + 16/116;
                z = z > 0.008856 ? Math.pow(z, 1/3) : (7.787 * z) + 16/116;

                return [
                    116 * y - 16,   // L
                    500 * (x - y),   // a
                    200 * (y - z)    // b
                ];
            }

            function rgbToHsv(r, g, b) {
                r /= 255; g /= 255; b /= 255;
                const max = Math.max(r, g, b);
                const min = Math.min(r, g, b);
                const d = max - min;
                let h, s = max === 0 ? 0 : d / max, v = max;

                if (max === min) {
                    h = 0;
                } else {
                    switch (max) {
                        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                        case g: h = (b - r) / d + 2; break;
                        case b: h = (r - g) / d + 4; break;
                    }
                    h /= 6;
                }
                return [h * 360, s * 100, v * 100];
            }

            function hsvToRgb(h, s, v) {
                h /= 360; s /= 100; v /= 100;
                let r, g, b;
                const i = Math.floor(h * 6);
                const f = h * 6 - i;
                const p = v * (1 - s);
                const q = v * (1 - f * s);
                const t = v * (1 - (1 - f) * s);

                switch (i % 6) {
                    case 0: r = v; g = t; b = p; break;
                    case 1: r = q; g = v; b = p; break;
                    case 2: r = p; g = v; b = t; break;
                    case 3: r = p; g = q; b = v; break;
                    case 4: r = t; g = p; b = v; break;
                    case 5: r = v; g = p; b = q; break;
                }

                return [
                    Math.round(r * 255),
                    Math.round(g * 255),
                    Math.round(b * 255)
                ];
            }

            // Calculate direct RGB distance
            function rgbDistance(r1, g1, b1, r2, g2, b2) {
                return Math.sqrt(
                    Math.pow(r1 - r2, 2) +
                    Math.pow(g1 - g2, 2) +
                    Math.pow(b1 - b2, 2)
                );
            }

            // Prepare all color mappings with their properties
            const processedMappings = colorMappings.map(mapping => {
                const originalColor = mapping.originalColor;
                const replacementColor = mapping.targetColor;
                
                console.log("Color replacement:", { 
                    original: originalColor, 
                    replacement: replacementColor 
                });
                
                // Get color properties
                const originalHsv = rgbToHsv(...originalColor);
                const replacementHsv = rgbToHsv(...replacementColor);
                const originalLab = rgbToLab(...originalColor);
                
                // Define if original color has special properties
                const isOriginalDark = originalHsv[2] < 20;
                const isOriginalLight = originalHsv[2] > 90 && originalHsv[1] < 15;
                const isOriginalGray = originalHsv[1] < 15;
                
                return {
                    originalColor,
                    replacementColor,
                    originalHsv,
                    replacementHsv,
                    originalLab,
                    isOriginalDark,
                    isOriginalLight,
                    isOriginalGray
                };
            });

            // Create a cache for color transformations
            const transformCache = new Map();

            // Define tolerances
            const RGB_TOLERANCE = 60;       // Direct RGB distance (0-441)
            const HUE_TOLERANCE = 15;       // Hue degrees (0-180)
            const SAT_TOLERANCE = 15;       // Saturation % (0-100)
            const VAL_TOLERANCE = 20;       // Value % (0-100)
            const LAB_TOLERANCE = 25;       // Lab distance

            // Process each pixel
            for (let i = 0; i < data.length; i += 4) {
                if (data[i + 3] < 128) continue; // Skip transparent pixels

                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                
                // Skip pure black for efficiency
                if (r <= 3 && g <= 3 && b <= 3) continue;
                
                // Create a key for the cache
                const colorKey = `${r},${g},${b}`;
                if (transformCache.has(colorKey)) {
                    const cachedColor = transformCache.get(colorKey);
                    data[i] = cachedColor[0];
                    data[i + 1] = cachedColor[1];
                    data[i + 2] = cachedColor[2];
                    continue;
                }
                
                // Find the best mapping for this color
                let bestMapping = null;
                let bestMatchScore = -1;
                
                for (const mapping of processedMappings) {
                    // Direct RGB distance - fastest check
                    const rgbDist = rgbDistance(r, g, b, 
                        mapping.originalColor[0], 
                        mapping.originalColor[1], 
                        mapping.originalColor[2]);
                    
                    // Skip if too far in RGB space for efficiency
                    if (rgbDist > RGB_TOLERANCE * 1.5) continue;
                    
                    // Calculate pixel color in HSV space
                    const pixelHsv = rgbToHsv(r, g, b);
                    
                    // Calculate hue distance (accounting for circularity)
                    let hueDist = Math.abs(pixelHsv[0] - mapping.originalHsv[0]);
                    if (hueDist > 180) hueDist = 360 - hueDist;
                    
                    // Determine if color is similar based on HSV
                    let isColorMatch = false;
                    
                    // Special case for grays, blacks, whites
                    if (mapping.isOriginalGray) {
                        // For gray colors, focus on brightness and saturation
                        isColorMatch = 
                            pixelHsv[1] < 20 && // Low saturation
                            Math.abs(pixelHsv[2] - mapping.originalHsv[2]) < VAL_TOLERANCE; // Similar brightness
                    } 
                    else if (mapping.isOriginalDark) {
                        // For dark colors, focus more on hue
                        isColorMatch = 
                            pixelHsv[2] < 25 && // Dark
                            (pixelHsv[1] < 20 || hueDist < HUE_TOLERANCE * 1.5); // Either unsaturated or similar hue
                    }
                    else if (mapping.isOriginalLight) {
                        // For light colors, focus more on hue
                        isColorMatch = 
                            pixelHsv[2] > 85 && // Light
                            pixelHsv[1] < 20;  // Low saturation
                    }
                    else {
                        // For normal colors, use stricter HSV matching
                        isColorMatch = 
                            hueDist < HUE_TOLERANCE && 
                            Math.abs(pixelHsv[1] - mapping.originalHsv[1]) < SAT_TOLERANCE &&
                            Math.abs(pixelHsv[2] - mapping.originalHsv[2]) < VAL_TOLERANCE;
                    }
                    
                    // If HSV check passes or RGB is close, do a more expensive Lab check
                    if (isColorMatch || rgbDist < RGB_TOLERANCE/2) {
                        const pixelLab = rgbToLab(r, g, b);
                        
                        const labDistance = Math.sqrt(
                            Math.pow(pixelLab[0] - mapping.originalLab[0], 2) +
                            Math.pow(pixelLab[1] - mapping.originalLab[1], 2) +
                            Math.pow(pixelLab[2] - mapping.originalLab[2], 2)
                        );
                        
                        // Calculate match score - lower is better
                        // Combine different metrics with appropriate weights
                        const rgbScore = rgbDist / RGB_TOLERANCE;
                        const labScore = labDistance / LAB_TOLERANCE;
                        const matchScore = rgbScore * 0.3 + labScore * 0.7;
                        
                        // If this is the best match so far, save it
                        if (matchScore < 1 && (bestMapping === null || matchScore < bestMatchScore)) {
                            bestMapping = mapping;
                            bestMatchScore = matchScore;
                        }
                    }
                }
                
                // If we found a mapping, apply color transformation
                if (bestMapping !== null) {
                    // Calculate pixel in HSV space for transformation
                    const pixelHsv = rgbToHsv(r, g, b);
                    
                    // Determine how close the match is
                    const exactMatch = bestMatchScore < 0.3;
                    
                    let newColor;
                    
                    if (exactMatch) {
                        // Direct replacement for very close matches
                        newColor = bestMapping.replacementColor;
                    } else {
                        // For less exact matches, transform while preserving variation
                        
                        // Calculate relative shifts
                        const hueDiff = bestMapping.replacementHsv[0] - bestMapping.originalHsv[0];
                        const satRatio = bestMapping.originalHsv[1] > 5 ? 
                                         bestMapping.replacementHsv[1] / bestMapping.originalHsv[1] : 1;
                        const valRatio = bestMapping.originalHsv[2] > 5 ? 
                                         bestMapping.replacementHsv[2] / bestMapping.originalHsv[2] : 1;
                        
                        // Apply transformations
                        let newHue = (pixelHsv[0] + hueDiff) % 360;
                        if (newHue < 0) newHue += 360;
                        
                        let newSat = Math.max(0, Math.min(100, pixelHsv[1] * satRatio));
                        let newVal = Math.max(0, Math.min(100, pixelHsv[2] * valRatio));
                        
                        // Convert back to RGB
                        newColor = hsvToRgb(newHue, newSat, newVal);
                    }
                    
                    // Apply new color
                    data[i] = newColor[0];
                    data[i + 1] = newColor[1];
                    data[i + 2] = newColor[2];
                    
                    // Cache this transformation
                    transformCache.set(colorKey, newColor);
                }
            }

            ctx.putImageData(imageDataObj, 0, 0);
            const dataUrl = canvasElement.toDataURL('image/png');
            console.timeEnd('colorMapping');
            resolve(dataUrl);
        };
        img.src = imageData;
    });
}


async applyMultipleColorMappings(imageData, colorMappings) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            console.time('colorMapping');
            const canvasElement = document.createElement('canvas');
            const ctx = canvasElement.getContext('2d');
            canvasElement.width = img.width;
            canvasElement.height = img.height;

            ctx.drawImage(img, 0, 0);
            const imageDataObj = ctx.getImageData(0, 0, img.width, img.height);
            const data = imageDataObj.data;
            const width = img.width;
            const height = img.height;

            // Color conversion utilities
            function rgbToHsv(r, g, b) {
                r /= 255; g /= 255; b /= 255;
                const max = Math.max(r, g, b);
                const min = Math.min(r, g, b);
                const d = max - min;
                let h, s = max === 0 ? 0 : d / max, v = max;

                if (max === min) {
                    h = 0;
                } else {
                    switch (max) {
                        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                        case g: h = (b - r) / d + 2; break;
                        case b: h = (r - g) / d + 4; break;
                    }
                    h /= 6;
                }
                return [h * 360, s * 100, v * 100];
            }

            function hsvToRgb(h, s, v) {
                h /= 360; s /= 100; v /= 100;
                let r, g, b;
                const i = Math.floor(h * 6);
                const f = h * 6 - i;
                const p = v * (1 - s);
                const q = v * (1 - f * s);
                const t = v * (1 - (1 - f) * s);

                switch (i % 6) {
                    case 0: r = v; g = t; b = p; break;
                    case 1: r = q; g = v; b = p; break;
                    case 2: r = p; g = v; b = t; break;
                    case 3: r = p; g = q; b = v; break;
                    case 4: r = t; g = p; b = v; break;
                    case 5: r = v; g = p; b = q; break;
                }

                return [
                    Math.round(r * 255),
                    Math.round(g * 255),
                    Math.round(b * 255)
                ];
            }
            
            // IMPROVED: More flexible color family detection for blurry images
            function sameColorFamily(color1, color2) {
                const [r1, g1, b1] = color1;
                const [r2, g2, b2] = color2;
                
                // Convert to HSV for better comparison
                const hsv1 = rgbToHsv(r1, g1, b1);
                const hsv2 = rgbToHsv(r2, g2, b2);
                
                // Check if both are achromatic (black, white, gray)
                const isAchromatic1 = hsv1[1] < 20; // More lenient threshold
                const isAchromatic2 = hsv2[1] < 20; 
                
                // If both are achromatic, compare by value (brightness)
                if (isAchromatic1 && isAchromatic2) {
                    // Allow more variance in brightness for achromatic colors
                    return Math.abs(hsv1[2] - hsv2[2]) < 40; // More lenient
                }
                
                // If one is achromatic and the other not, they're different families
                if (isAchromatic1 !== isAchromatic2) {
                    return false;
                }
                
                // For chromatic colors, check hue similarity with adaptive threshold
                // Calculate hue difference with wrap-around
                let hueDiff = Math.abs(hsv1[0] - hsv2[0]);
                if (hueDiff > 180) hueDiff = 360 - hueDiff;
                
                // For very dark or low saturation colors, hue is less reliable
                const areBothDark = hsv1[2] < 35 && hsv2[2] < 35;
                const lowSaturation = hsv1[1] < 40 || hsv2[1] < 40;
                
                // Adapt thresholds based on color properties
                // CHANGE: Tighter hue threshold (40 → 30) for better handling of many colors
                const hueThreshold = areBothDark || lowSaturation ? 45 : 30;
                const satThreshold = areBothDark ? 50 : 40;
                
                // Colors in the same family should have similar hue and not too different saturation
                return hueDiff < hueThreshold && 
                       Math.abs(hsv1[1] - hsv2[1]) < satThreshold;
            }
            
            // IMPROVED: Better gradient detection for blurry images
            function detectGradients() {
                // Store gradient information
                const gradientMap = new Array(width * height).fill(false);
                const gradientStrengthMap = new Array(width * height).fill(0);
                
                // First pass: detect gradient pixels with more sensitivity
                for (let y = 1; y < height - 1; y++) {
                    for (let x = 1; x < width - 1; x++) {
                        const centerIdx = (y * width + x) * 4;
                        if (data[centerIdx + 3] < 128) continue; // Skip transparent
                        
                        const centerColor = [data[centerIdx], data[centerIdx + 1], data[centerIdx + 2]];
                        const centerHsv = rgbToHsv(...centerColor);
                        
                        // Adaptive thresholds - more sensitive for blurry images
                        const minDiffThreshold = Math.max(2, 5 - centerHsv[1] * 0.05);
                        const maxDiffThreshold = 60 + (1 - centerHsv[1]/100) * 20;
                        
                        // Check neighbors
                        let maxDiff = 0;
                        let hasGradient = false;
                        
                        // Check in all directions for better detection
                        const directions = [
                            { dx: -1, dy: 0 }, { dx: 1, dy: 0 },
                            { dx: 0, dy: -1 }, { dx: 0, dy: 1 },
                            { dx: -1, dy: -1 }, { dx: 1, dy: -1 },
                            { dx: -1, dy: 1 }, { dx: 1, dy: 1 }
                        ];
                        
                        for (const { dx, dy } of directions) {
                            const nx = x + dx;
                            const ny = y + dy;
                            
                            if (nx < 0 || nx >= width || ny < 0 || ny >= height) continue;
                            
                            const neighborIdx = (ny * width + nx) * 4;
                            if (data[neighborIdx + 3] < 128) continue;
                            
                            const neighborColor = [data[neighborIdx], data[neighborIdx + 1], data[neighborIdx + 2]];
                            
                            // Calculate color difference
                            const diff = Math.sqrt(
                                Math.pow(centerColor[0] - neighborColor[0], 2) +
                                Math.pow(centerColor[1] - neighborColor[1], 2) +
                                Math.pow(centerColor[2] - neighborColor[2], 2)
                            );
                            
                            // More relaxed condition for gradients
                            if (diff > minDiffThreshold && diff < maxDiffThreshold) {
                                // For very subtle gradients, don't strictly require same family
                                if (diff < 15 || sameColorFamily(centerColor, neighborColor)) {
                                    hasGradient = true;
                                    maxDiff = Math.max(maxDiff, diff);
                                }
                            }
                        }
                        
                        if (hasGradient) {
                            gradientMap[y * width + x] = true;
                            gradientStrengthMap[y * width + x] = Math.min(1, maxDiff / maxDiffThreshold);
                        }
                    }
                }
                
                // Second pass: expand gradient regions more aggressively
                const expandedGradientMap = [...gradientMap];
                
                // Multiple expansion passes for better coverage
                for (let pass = 0; pass < 2; pass++) {
                    for (let y = 1; y < height - 1; y++) {
                        for (let x = 1; x < width - 1; x++) {
                            const pixelIndex = y * width + x;
                            if (expandedGradientMap[pixelIndex] || data[(pixelIndex * 4) + 3] < 128) continue;
                            
                            // Check if surrounded by gradient pixels
                            let gradientNeighbors = 0;
                            
                            for (let dy = -2; dy <= 2; dy++) {
                                for (let dx = -2; dx <= 2; dx++) {
                                    if (dx === 0 && dy === 0) continue;
                                    
                                    const nx = x + dx;
                                    const ny = y + dy;
                                    
                                    if (nx < 0 || nx >= width || ny < 0 || ny >= height) continue;
                                    
                                    const nIndex = ny * width + nx;
                                    
                                    if (expandedGradientMap[nIndex]) {
                                        // Weight by distance
                                        gradientNeighbors += (Math.abs(dx) + Math.abs(dy) <= 2) ? 1 : 0.5;
                                    }
                                }
                            }
                            
                            // More aggressive expansion for blurry images
                            if (gradientNeighbors >= 1.5) {
                                expandedGradientMap[pixelIndex] = true;
                                gradientStrengthMap[pixelIndex] = 0.6;
                            }
                        }
                    }
                }
                
                return { gradientMap: expandedGradientMap, gradientStrengthMap };
            }
            
            // Identify color families with improved logic
            function identifyColorFamilies() {
                const colorFamilies = [];
                const pixelFamilyMap = new Array(width * height).fill(-1);
                
                // Process pixels to form initial color families
                for (let y = 0; y < height; y++) {
                    for (let x = 0; x < width; x++) {
                        const pixelIndex = y * width + x;
                        const colorIdx = pixelIndex * 4;
                        
                        if (data[colorIdx + 3] < 128) continue; // Skip transparent
                        
                        // Skip if already assigned to a family
                        if (pixelFamilyMap[pixelIndex] !== -1) continue;
                        
                        const pixelColor = [data[colorIdx], data[colorIdx + 1], data[colorIdx + 2]];
                        
                        // Only skip pure black (almost zero in all channels)
                        if (pixelColor[0] <= 3 && pixelColor[1] <= 3 && pixelColor[2] <= 3) continue;
                        
                        // CHANGE: For many colors, be more selective about family membership
                        // Check if this color fits into an existing family with stricter thresholds
                        let foundFamily = false;
                        
                        // CHANGE: Only check recent families first to improve performance with many colors
                        const startIdx = Math.max(0, colorFamilies.length - 50);
                        for (let i = startIdx; i < colorFamilies.length; i++) {
                            const family = colorFamilies[i];
                            
                            // Check if color belongs to this family with improved detection
                            if (sameColorFamily(pixelColor, family.referenceColor)) {
                                // Add to family
                                family.pixels.push(pixelIndex);
                                family.sumR += pixelColor[0];
                                family.sumG += pixelColor[1];
                                family.sumB += pixelColor[2];
                                family.count++;
                                
                                pixelFamilyMap[pixelIndex] = i;
                                foundFamily = true;
                                break;
                            }
                        }
                        
                        // If no matching family in recent ones, check older ones
                        if (!foundFamily && startIdx > 0) {
                            for (let i = 0; i < startIdx; i++) {
                                const family = colorFamilies[i];
                                
                                if (sameColorFamily(pixelColor, family.referenceColor)) {
                                    // Add to family
                                    family.pixels.push(pixelIndex);
                                    family.sumR += pixelColor[0];
                                    family.sumG += pixelColor[1];
                                    family.sumB += pixelColor[2];
                                    family.count++;
                                    
                                    pixelFamilyMap[pixelIndex] = i;
                                    foundFamily = true;
                                    break;
                                }
                            }
                        }
                        
                        // If no matching family, create a new one
                        if (!foundFamily) {
                            const familyIndex = colorFamilies.length;
                            colorFamilies.push({
                                referenceColor: pixelColor,
                                pixels: [pixelIndex],
                                sumR: pixelColor[0],
                                sumG: pixelColor[1],
                                sumB: pixelColor[2],
                                count: 1,
                                mappingIndex: -1 // Will be set later
                            });
                            
                            pixelFamilyMap[pixelIndex] = familyIndex;
                        }
                    }
                }
                
                // Calculate average color for each family
                colorFamilies.forEach(family => {
                    family.avgColor = [
                        Math.round(family.sumR / family.count),
                        Math.round(family.sumG / family.count),
                        Math.round(family.sumB / family.count)
                    ];
                    
                    // Also calculate HSV for easier comparisons
                    family.hsv = rgbToHsv(...family.avgColor);
                });
                
                console.log(`Identified ${colorFamilies.length} color families`);
                return { colorFamilies, pixelFamilyMap };
            }
            
            // Process color mappings
            function prepareColorMappings() {
                return colorMappings.map((mapping, index) => {
                    const { originalColor, targetColor } = mapping;
                    
                    // Convert to HSV for easier transformations
                    const originalHsv = rgbToHsv(...originalColor);
                    const targetHsv = rgbToHsv(...targetColor);
                    
                    // Calculate transformation parameters more explicitly
                    let hueShift = targetHsv[0] - originalHsv[0];
                    if (hueShift > 180) hueShift -= 360;
                    else if (hueShift < -180) hueShift += 360;
                    
                    // Calculate more precise ratios to maintain the exact relationship
                    const satRatio = originalHsv[1] > 5 ? targetHsv[1] / originalHsv[1] : 1;
                    const valRatio = originalHsv[2] > 5 ? targetHsv[2] / originalHsv[2] : 1;
                    
                    // Include the original button reference to maintain the exact mapping relationship
                    return {
                        originalColor,
                        targetColor,
                        originalHsv,
                        targetHsv,
                        hueShift,
                        satRatio,
                        valRatio,
                        index,
                        buttonReference: mapping.button // Store the button reference
                    };
                });
            }
            
            // IMPROVED: Better mapping for more colors
            function mapFamiliesToMappings(colorFamilies, processedMappings) {
                // CHANGE: For each color family, find the best matching source color
                // When dealing with many colors, we need more precise mapping
                colorFamilies.forEach(family => {
                    let bestMappingIndex = -1;
                    let bestScore = Infinity;
                    
                    for (let i = 0; i < processedMappings.length; i++) {
                        const mapping = processedMappings[i];
                        
                        // Calculate weighted distance in both RGB and HSV space
                        // RGB distance for precise matching
                        const rgbDistance = Math.sqrt(
                            Math.pow(family.avgColor[0] - mapping.originalColor[0], 2) +
                            Math.pow(family.avgColor[1] - mapping.originalColor[1], 2) +
                            Math.pow(family.avgColor[2] - mapping.originalColor[2], 2)
                        );
                        
                        // HSV comparison for perceptual matching
                        const familyHsv = family.hsv;
                        const mappingHsv = mapping.originalHsv;
                        
                        // Calculate hue difference with wrap-around
                        let hueDiff = Math.abs(familyHsv[0] - mappingHsv[0]);
                        if (hueDiff > 180) hueDiff = 360 - hueDiff;
                        
                        // Weight the components differently
                        const isAchromatic = familyHsv[1] < 15 || mappingHsv[1] < 15;
                        
                        let score;
                        if (isAchromatic) {
                            // For achromatic colors, focus on brightness
                            score = (rgbDistance * 0.3) + (Math.abs(familyHsv[2] - mappingHsv[2]) * 2);
                        } else {
                            // For chromatic colors, prioritize hue match
                            score = (rgbDistance * 0.3) + (hueDiff * 0.5) + 
                                    (Math.abs(familyHsv[1] - mappingHsv[1]) * 0.3) + 
                                    (Math.abs(familyHsv[2] - mappingHsv[2]) * 0.2);
                        }
                        
                        if (score < bestScore) {
                            bestScore = score;
                            bestMappingIndex = i;
                        }
                    }
                    
                    // CHANGE: Use a threshold that scales with the number of color mappings
                    // More colors need more relaxed threshold to ensure proper mapping
                    const threshold = 60 + Math.min(40, processedMappings.length * 2);
                    
                    if (bestScore < threshold) {
                        family.mappingIndex = bestMappingIndex;
                    } else {
                        // For families without a good match, leave unmapped
                        family.mappingIndex = -1;
                    }
                });
            }
            
            // IMPROVED: Better color transformation logic
            function transformColor(r, g, b, mappingIndex, isGradient = false, gradientStrength = 0) {
                // Get the mapping
                const mapping = processedMappings[mappingIndex];
                
                // Get color in HSV space
                const pixelHsv = rgbToHsv(r, g, b);
                
                // Check if colors are very close to the original mapping color
                const originalRGB = mapping.originalColor;
                const rgbDistance = Math.sqrt(
                    Math.pow(r - originalRGB[0], 2) +
                    Math.pow(g - originalRGB[1], 2) +
                    Math.pow(b - originalRGB[2], 2)
                );
                
                // If very close to original color, use target color directly
                if (rgbDistance < 10) {
                    return mapping.targetColor;
                }
                
                // Check if color is achromatic (low saturation)
                const isAchromatic = pixelHsv[1] < 15;
                const isDark = pixelHsv[2] < 30;
                
                // Calculate relative brightness compared to the original mapping color
                // This is crucial for preserving shading and transparency effects
                const relativeBrightness = mapping.originalHsv[2] > 0 ? 
                    pixelHsv[2] / mapping.originalHsv[2] : 1;
                
                // Calculate hue difference with wrap-around handling
                let hueDiff = ((pixelHsv[0] - mapping.originalHsv[0] + 360) % 360);
                hueDiff = hueDiff > 180 ? hueDiff - 360 : hueDiff;
                
                // For saturation, calculate the relative value
                const relativeSaturation = mapping.originalHsv[1] > 0 ? 
                    pixelHsv[1] / mapping.originalHsv[1] : 1;
                
                // Different transformation strategy based on pixel characteristics
                let newHue, newSat, newVal;
                
                if (isAchromatic) {
                    // For grayscale, adopt target hue but preserve relative brightness
                    newHue = mapping.targetHsv[0];
                    
                    // Keep very low saturation for achromatic colors
                    newSat = Math.min(10, pixelHsv[1]);
                    
                    // Crucial: Preserve relative brightness for shading effects
                    newVal = Math.max(0, Math.min(100, mapping.targetHsv[2] * relativeBrightness));
                } 
                else if (isGradient) {
                    // For gradients, preserve the relative brightness even more carefully
                    
                    // Use target hue but adjust based on original variations for natural gradients
                    newHue = (mapping.targetHsv[0] + hueDiff * 0.3) % 360;
                    if (newHue < 0) newHue += 360;
                    
                    // Blend saturation but respect original variations
                    newSat = Math.max(5, Math.min(100, mapping.targetHsv[1] * relativeSaturation));
                    
                    // Most important: accurately preserve relative brightness
                    newVal = Math.max(0, Math.min(100, mapping.targetHsv[2] * relativeBrightness));
                } 
                else {
                    // For regular pixels, carefully preserve shading
                    if (isDark) {
                        // For dark areas, maintain darkness but use target hue
                        newHue = mapping.targetHsv[0];
                        newSat = Math.min(100, mapping.targetHsv[1] * 0.7);
                        
                        // Preserve darkness but map to target's darkness range
                        // This ensures dark areas remain distinguishable but adopt target color
                        newVal = Math.max(0, Math.min(40, mapping.targetHsv[2] * relativeBrightness));
                    } 
                    else {
                        // For normal colors, preserve shading variations
                        newHue = mapping.targetHsv[0];
                        
                        // Maintain saturation relationship to preserve texture
                        newSat = Math.max(0, Math.min(100, mapping.targetHsv[1] * relativeSaturation));
                        
                        // Crucial: accurately preserve brightness relationships
                        newVal = Math.max(0, Math.min(100, mapping.targetHsv[2] * relativeBrightness));
                    }
                }
                
                // Convert back to RGB
                return hsvToRgb(newHue, newSat, newVal);
            }
            
            // Main processing pipeline
            
            // Step 1: Detect gradients
            console.log("Detecting gradients...");
            const { gradientMap, gradientStrengthMap } = detectGradients();
            
            // Step 2: Identify color families
            console.log("Identifying color families...");
            const { colorFamilies, pixelFamilyMap } = identifyColorFamilies();
            
            // Step 3: Process mappings
            console.log("Processing color mappings...");
            const processedMappings = prepareColorMappings();
            
            // Step 4: Map families to mappings - IMPROVED for more colors
            console.log("Mapping color families to target colors...");
            mapFamiliesToMappings(colorFamilies, processedMappings);
            
            // CHANGE: Set a better default mapping for unmatched pixels
            // Find the most dominant mapping by counting pixels
            let mappingCounts = new Array(processedMappings.length).fill(0);
            colorFamilies.forEach(family => {
                if (family.mappingIndex !== -1) {
                    mappingCounts[family.mappingIndex] += family.count;
                }
            });
            
            let defaultMappingIndex = 0;
            let maxCount = mappingCounts[0];
            for (let i = 1; i < mappingCounts.length; i++) {
                if (mappingCounts[i] > maxCount) {
                    maxCount = mappingCounts[i];
                    defaultMappingIndex = i;
                }
            }
            
            console.log("Transforming colors...");

            // Use a cache for processed colors
            const transformCache = new Map();

            // Apply transformations
            for (let i = 0; i < data.length; i += 4) {
                if (data[i + 3] < 128) continue; // Skip transparent
                
                const r = data[i], g = data[i + 1], b = data[i + 2];
                
                // Only skip absolute black
                if (r <= 3 && g <= 3 && b <= 3) continue;
                
                const pixelIndex = Math.floor(i / 4);
                const familyIndex = pixelFamilyMap[pixelIndex];
                
                // Determine which mapping to use, with fallback for unassigned pixels
                let mappingToUse = defaultMappingIndex;
                
                if (familyIndex !== -1 && familyIndex < colorFamilies.length) {
                    const family = colorFamilies[familyIndex];
                    if (family.mappingIndex !== -1) {
                        mappingToUse = family.mappingIndex;
                    } else {
                        // CHANGE: For families with no mapping, find closest mapping directly
                        // This helps with more accurate color matching for many colors
                        const pixelHsv = rgbToHsv(r, g, b);
                        let bestDistance = Infinity;
                        
                        for (let j = 0; j < processedMappings.length; j++) {
                            const mappingHsv = processedMappings[j].originalHsv;
                            
                            // Weighted distance calculation for perceptual matching
                            let hueDiff = Math.abs(pixelHsv[0] - mappingHsv[0]);
                            if (hueDiff > 180) hueDiff = 360 - hueDiff;
                            
                            // For low saturation, focus on brightness
                            const distance = (pixelHsv[1] < 15 || mappingHsv[1] < 15) ? 
                                Math.abs(pixelHsv[2] - mappingHsv[2]) / 100 :
                                (hueDiff / 180) * 0.6 + 
                                Math.abs(pixelHsv[1] - mappingHsv[1]) / 100 * 0.2 + 
                                Math.abs(pixelHsv[2] - mappingHsv[2]) / 100 * 0.2;
                            
                            if (distance < bestDistance) {
                                bestDistance = distance;
                                mappingToUse = j;
                            }
                        }
                    }
                }
                
                // Check cache for this color and mapping combination
                const colorKey = `${r},${g},${b},${mappingToUse}`;
                if (transformCache.has(colorKey)) {
                    const cachedColor = transformCache.get(colorKey);
                    data[i] = cachedColor[0];
                    data[i + 1] = cachedColor[1];
                    data[i + 2] = cachedColor[2];
                    continue;
                }
                
                // Check if this pixel is part of a gradient
                const isGradient = gradientMap[pixelIndex];
                const gradientStrength = gradientStrengthMap[pixelIndex];
                
                // Transform the color
                const newColor = transformColor(r, g, b, mappingToUse, isGradient, gradientStrength);
                
                // Apply the transformed color
                data[i] = newColor[0];
                data[i + 1] = newColor[1];
                data[i + 2] = newColor[2];
                
                // Cache this transformation
                // CHANGE: Limit cache size to prevent memory issues with many colors
                if (transformCache.size < 100000) {
                    transformCache.set(colorKey, newColor);
                }
            }

            console.log("Finished color mapping!");

            // Apply the changes to the canvas
            ctx.putImageData(imageDataObj, 0, 0);
            const dataUrl = canvasElement.toDataURL('image/png');
            console.timeEnd('colorMapping');
            resolve(dataUrl);
        };
        img.src = imageData;
    });
}  