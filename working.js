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