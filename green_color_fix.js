// FIXED: Collection-specific settings - GREEN COLORS ENABLED
const collectionSettings = {
    'ss': {
        saturationMultiplier: 1.5,
        lightnessMultiplier: 1.3,
        minSaturation: 75,
        maxSaturation: 100,
        minLightness: 55,
        maxLightness: 95,
        preferredFamilies: ['cyan', 'yellow', 'pink', 'orange', 'red', 'blue', 'purple', 'green'] // GREEN ADDED
    },
    'aw': {
        saturationMultiplier: 0.6,
        lightnessMultiplier: 0.75,
        minSaturation: 20,
        maxSaturation: 65,
        minLightness: 15,
        maxLightness: 65,
        preferredFamilies: ['purple', 'blue', 'red', 'orange', 'pink', 'cyan', 'green'] // GREEN ADDED
    },
    'trending': {
        saturationMultiplier: 1.0,
        lightnessMultiplier: 1.0,
        minSaturation: 35,
        maxSaturation: 85,
        minLightness: 30,
        maxLightness: 80,
        preferredFamilies: ['red', 'orange', 'green', 'yellow', 'cyan', 'blue', 'purple', 'pink']
    }
};

// FIXED: getCollectionSpecificFamily - GREEN ENABLED (30% exclusion instead of 80%)
function getCollectionSpecificFamily(collection, paletteIndex, colorIndex, familyPool, usedFamilies, originalFamily) {
    let targetFamily;
    
    // Include green in the pool normally - REDUCED EXCLUSION
    const poolWithoutGreen = familyPool.filter(f => f !== 'green');
    const effectivePool = Math.random() < 0.3 ? poolWithoutGreen : familyPool; // 30% chance to exclude green (was 80%)
    
    const poolIndex = effectivePool.indexOf(originalFamily);
    const totalFamilies = effectivePool.length;
    
    if (collection === 'ss') {
        const strategies = [
            () => effectivePool[(poolIndex + 2) % totalFamilies],
            () => effectivePool[(poolIndex + 3) % totalFamilies],
            () => effectivePool[(poolIndex + 4) % totalFamilies],
            () => ['cyan', 'yellow', 'pink', 'green'][colorIndex % 4] // GREEN ADDED
        ];
        targetFamily = strategies[paletteIndex % strategies.length]();
    } else if (collection === 'aw') {
        const strategies = [
            () => originalFamily,
            () => effectivePool[(poolIndex + 1) % totalFamilies],
            () => effectivePool[(poolIndex - 1 + totalFamilies) % totalFamilies],
            () => ['purple', 'blue', 'red', 'green'][colorIndex % 4] // GREEN ADDED
        ];
        targetFamily = strategies[paletteIndex % strategies.length]();
    } else {
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

// FIXED: generateDiversePalettes - GREEN HANDLING (80% inclusion for trending, 60% for others)
// Replace the green handling section in generateDiversePalettes with this:
/*
    // Allow green colors normally - INCREASED GREEN CHANCE
    if (originalFamily === 'green') {
        // Allow green in most cases - REVERSED LOGIC
        const greenChance = collection === 'trending' ? 0.8 : 0.6; // Was 0.2 and 0.1
        if (Math.random() < greenChance) {
            targetFamily = 'green';
        } else {
            // Occasionally replace green with other colors
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
*/

// FIXED: generateMatchingColor - Keep the olive green prevention but reduce minimum saturation
// In generateMatchingColor function, replace the green handling with:
/*
    // Prevent very dull olive greens but allow natural greens
    if (targetHueRange === 'green') {
        newSat = Math.max(40, Math.min(100, sourceS + (Math.random() - 0.3) * 30)); // Reduced from 60 to 40
        newLight = Math.max(30, Math.min(80, sourceL + (Math.random() - 0.5) * 20));
        
        // Only shift away from very muddy olive (narrower range)
        if (h >= 78 && h < 82 && newSat < 35) {
            h = h < 80 ? 75 : 85;
        }
    }
*/
