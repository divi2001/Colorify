function generateDiversePalettes(baseColors, collection = 'trending') {
    const palettes = [];
    
    // Group base colors by families
    const baseFamilies = groupColorsByFamily(baseColors);
    const availableFamilyNames = Object.keys(baseFamilies);
    
    // All possible target families - REDUCED GREEN PRESENCE
    const warmFamilies = ['red', 'orange', 'yellow', 'pink'];
    const coolFamilies = ['cyan', 'blue', 'purple']; // REMOVED GREEN from cool families
    const allFamilies = [...warmFamilies, ...coolFamilies];
    
    // Collection-specific adjustments - REDUCE GREEN GENERATION
    const collectionSettings = {
        'ss': {
            saturationMultiplier: 1.3,
            lightnessMultiplier: 1.2,
            minSaturation: 70,
            maxSaturation: 100,
            minLightness: 50,
            maxLightness: 95,
            preferredFamilies: ['cyan', 'yellow', 'pink', 'orange', 'red', 'blue', 'purple'] // NO GREEN
        },
        'aw': {
            saturationMultiplier: 0.7,
            lightnessMultiplier: 0.85,
            minSaturation: 15,
            maxSaturation: 70,
            minLightness: 20,
            maxLightness: 70,
            preferredFamilies: ['purple', 'blue', 'red', 'orange', 'pink', 'cyan'] // NO GREEN
        },
        'trending': {
            saturationMultiplier: 1.0,
            lightnessMultiplier: 1.0,
            minSaturation: 30,
            maxSaturation: 90,
            minLightness: 30,
            maxLightness: 85,
            preferredFamilies: ['red', 'orange', 'yellow', 'cyan', 'blue', 'purple', 'pink'] // GREEN LIMITED
        }
    };
    
    const settings = collectionSettings[collection] || collectionSettings.trending;
    
    // Generate 20 unique palettes with REDUCED GREEN
    for (let i = 0; i < 20; i++) {
        const newPalette = [];
        const familyMapping = {};
        const usedTargetFamilies = new Set();
        
        // For each original family, assign a new target family
        availableFamilyNames.forEach((originalFamily, index) => {
            let targetFamily;
            
            // SPECIAL HANDLING FOR GREEN - REPLACE IT MORE AGGRESSIVELY
            if (originalFamily === 'green') {
                // Only allow green in 20% of cases for trending, 10% for others
                const greenChance = collection === 'trending' ? 0.2 : 0.1;
                if (Math.random() < greenChance) {
                    targetFamily = 'green';
                } else {
                    // Replace green with other colors
                    const greenReplacements = collection === 'ss' 
                        ? ['cyan', 'blue', 'yellow'] 
                        : collection === 'aw' 
                            ? ['purple', 'blue', 'red'] 
                            : ['cyan', 'blue', 'purple'];
                    targetFamily = greenReplacements[Math.floor(Math.random() * greenReplacements.length)];
                }
            } else {
                // Normal replacement for other colors
                targetFamily = getCollectionSpecificFamily(collection, i, index, settings.preferredFamilies, usedTargetFamilies, originalFamily);
            }
            
            familyMapping[originalFamily] = targetFamily;
            usedTargetFamilies.add(targetFamily);
        });
        
        // Generate new colors with collection-specific adjustments
        baseColors.forEach((originalColor, colorIndex) => {
            const originalFamily = getColorFamily(originalColor);
            const targetFamily = familyMapping[originalFamily] || settings.preferredFamilies[0];
            
            let newColor = generateMatchingColor(originalColor, targetFamily);
            let [h, s, l] = rgbToHsl(...newColor);
            
            // PREVENT OLIVE GREEN (low saturation yellow-green)
            if (targetFamily === 'green') {
                // Force green to be more vibrant, less olive-like
                s = Math.max(60, s); // Minimum saturation for green
                // Shift hue away from olive range (75-85 is olive territory)
                if (h >= 75 && h < 85) {
                    h = h < 80 ? 70 : 90; // Push to brighter green or yellow-green
                }
            }
            
            const variations = getCollectionVariations(collection, i, colorIndex);
            
            // Apply adjustments and variations
            s = Math.max(settings.minSaturation, Math.min(settings.maxSaturation, 
                s * settings.saturationMultiplier + variations.sat));
            l = Math.max(settings.minLightness, Math.min(settings.maxLightness, 
                l * settings.lightnessMultiplier + variations.light));
            
            const newHue = (h + variations.hue + 360) % 360;
            
            // Background color handling
            if (isBackgroundColor(originalColor)) {
                if (collection === 'ss') {
                    newColor = hslToRgb(newHue, Math.min(20, s), Math.max(92, l));
                } else if (collection === 'aw') {
                    newColor = hslToRgb(newHue, Math.min(15, s), Math.min(70, Math.max(60, l)));
                } else {
                    newColor = hslToRgb(newHue, Math.min(20, s), Math.max(85, l));
                }
            } else {
                newColor = hslToRgb(newHue, s, l);
            }
            
            newPalette.push(newColor);
        });
        
        palettes.push(newPalette);
    }
    
    return palettes;
}

// Enhanced family selection to avoid green
function getCollectionSpecificFamily(collection, paletteIndex, colorIndex, familyPool, usedFamilies, originalFamily) {
    let targetFamily;
    
    // Create a pool without green for most cases
    const poolWithoutGreen = familyPool.filter(f => f !== 'green');
    const effectivePool = Math.random() < 0.8 ? poolWithoutGreen : familyPool; // 80% chance to exclude green
    
    const poolIndex = effectivePool.indexOf(originalFamily);
    const totalFamilies = effectivePool.length;
    
    if (collection === 'ss') {
        // SS: Bright families, avoid green
        const strategies = [
            () => effectivePool[(poolIndex + 2) % totalFamilies],
            () => effectivePool[(poolIndex + 3) % totalFamilies],
            () => effectivePool[(poolIndex + 4) % totalFamilies],
            () => ['cyan', 'yellow', 'pink'][colorIndex % 3]
        ];
        targetFamily = strategies[paletteIndex % strategies.length]();
    } 
    else if (collection === 'aw') {
        // AW: Rich families, avoid green
        const strategies = [
            () => originalFamily,
            () => effectivePool[(poolIndex + 1) % totalFamilies],
            () => effectivePool[(poolIndex - 1 + totalFamilies) % totalFamilies],
            () => ['purple', 'blue', 'red'][colorIndex % 3]
        ];
        targetFamily = strategies[paletteIndex % strategies.length]();
    } 
    else {
        // Trending: Mixed approach with limited green
        if (paletteIndex < 10) {
            targetFamily = effectivePool[(poolIndex + paletteIndex) % totalFamilies];
        } else {
            targetFamily = effectivePool[(poolIndex * 2 + paletteIndex) % totalFamilies];
        }
    }
    
    // Ensure unique families in palette
    let attempts = 0;
    while (usedFamilies.has(targetFamily) && attempts < totalFamilies * 2) {
        targetFamily = effectivePool[(effectivePool.indexOf(targetFamily) + 1) % totalFamilies];
        attempts++;
    }
    
    return targetFamily;
}

// Also update the generateMatchingColor function to avoid olive green
function generateMatchingColor(sourceColor, targetHueRange) {
    const [sourceH, sourceS, sourceL] = rgbToHsl(...sourceColor);
    const isSourceBackground = isBackgroundColor(sourceColor);
    
    // Define hue ranges for each color family
    const hueRanges = {
        'red': [345, 15],
        'orange': [15, 45],
        'yellow': [45, 75],
        'green': [85, 150], // NARROWED range to avoid yellow-green and blue-green
        'cyan': [165, 195],
        'blue': [195, 255],
        'purple': [255, 285],
        'pink': [285, 345]
    };
    
    const range = hueRanges[targetHueRange];
    if (!range) {
        return hslToRgb(Math.random() * 360, sourceS, sourceL);
    }
    
    // Generate hue within the target family range
    let newHue;
    if (targetHueRange === 'red' && range[0] > range[1]) {
        if (Math.random() > 0.5) {
            newHue = range[0] + Math.random() * (360 - range[0]);
        } else {
            newHue = Math.random() * range[1];
        }
    } else {
        newHue = range[0] + Math.random() * (range[1] - range[0]);
    }
    
    // For green specifically, ensure good saturation to avoid olive
    let newSat = sourceS;
    let newLight = sourceL;
    
    if (targetHueRange === 'green') {
        newSat = Math.max(50, Math.min(100, sourceS + (Math.random() - 0.3) * 30)); // Higher min saturation
        newLight = Math.max(30, Math.min(80, sourceL + (Math.random() - 0.5) * 20)); // Better lightness range
    } else {
        newSat = Math.max(5, Math.min(100, sourceS + (Math.random() - 0.5) * 20));
        newLight = Math.max(5, Math.min(95, sourceL + (Math.random() - 0.5) * 15));
    }
    
    if (isSourceBackground) {
        return hslToRgb(newHue, Math.max(0, Math.min(15, newSat)), Math.max(80, Math.min(95, newLight)));
    } else {
        return hslToRgb(newHue, newSat, newLight);
    }
}