async function displayColorPalette(layerIndex, colors, collection = 'trending', maxVisibleColors = 6, totalLayers = 1) {
    const prefix = collection + '_';
    const MAX_DISPLAY_COUNT = 8; // Maximum number of colors to display
    const MIN_DISPLAY_COUNT = 4; // Minimum number of colors to display
    
    // ... [keep all your existing helper functions unchanged] ...
    
    // Main processing logic for single layer
    if (totalLayers === 1) {
        // NEW: Generate special palettes for first 5 (hue-shifted) and regular for the rest
        let allPalettes = [];
        
        // First 5 palettes: Use hue shifting
        const hueShiftedPalettes = generateHueShiftedPalettes(validatedColors, collection);
        allPalettes = [...hueShiftedPalettes];
        
        // FIXED: Generate diverse palettes ONCE and reuse them
        const diversePalettes = generateDiversePalettes(validatedColors);
        allPalettes = [...allPalettes, ...diversePalettes.slice(0, 20)];
        
        // Initialize the storage if needed BEFORE creating containers
        window[`${collection}PaletteColors`] = window[`${collection}PaletteColors`] || {};
        window[`${collection}PaletteHueShifted`] = window[`${collection}PaletteHueShifted`] || {};
        
        // STORE ALL PALETTES FIRST before creating UI
        for (let i = 0; i < 25; i++) {
            let paletteColors = allPalettes[i] || allPalettes[0];
            
            // Verify that all colors are valid
            paletteColors = paletteColors.filter(color => 
                Array.isArray(color) && 
                color.length === 3 && 
                color.every(v => typeof v === 'number' && !isNaN(v) && v >= 0 && v <= 255)
            );
            
            // If somehow we lost all colors, generate new ones
            if (paletteColors.length === 0) {
                paletteColors = [];
                for (let j = 0; j < 9; j++) {
                    const hue = j * (360 / 9);
                    paletteColors.push(hslToRgb(hue, 70 + Math.random() * 30, 45 + Math.random() * 25));
                }
            }
            
            // Store ALL colors in the palette data structure
            window[`${collection}PaletteColors`][i] = [...paletteColors];
            
            // Mark hue-shifted palettes with special flag
            if (i < 5) {
                window[`${collection}PaletteHueShifted`][i] = true;
            }
        }
        
        // Initialize preview cache if needed
        if (!window.palettePreviewCache) {
            window.palettePreviewCache = {};
        }
        if (!window.palettePreviewCache[collection]) {
            window.palettePreviewCache[collection] = {};
        }
        
        // Create preview canvases if they don't exist
        if (!window.previewCanvases) {
            window.previewCanvases = {};
            
            // Generate a smaller version of the original image for preview
            const originalCanvas = document.getElementById('layer_canvas_1');
            if (originalCanvas) {
                const previewCanvas = document.createElement('canvas');
                previewCanvas.width = 200;
                previewCanvas.height = 200;
                const previewCtx = previewCanvas.getContext('2d', { willReadFrequently: true });
                
                // Draw the original image scaled down
                previewCtx.drawImage(originalCanvas, 0, 0, 200, 200);
                
                // Store the preview canvas data URL for future use
                window.previewCanvases['original'] = previewCanvas.toDataURL();
            }
        }
        
        // Create all palette containers
        const paletteContainers = [];
        
        for (let i = 0; i < 25; i++) {
            const paletteContainer = document.getElementById(`${prefix}colorPalette_${i}`);
            if (!paletteContainer) continue;
            
            paletteContainer.innerHTML = '';
            
            // FIXED: Get palette colors from STORED data, not generating new ones
            const paletteColors = window[`${collection}PaletteColors`][i];
            
            if (!paletteColors || paletteColors.length === 0) {
                console.error(`No stored palette found for ${collection}[${i}]`);
                continue;
            }
            
            // Create container for the palette that includes preview
            const clickableContainer = document.createElement('div');
            clickableContainer.classList.add('palette-clickable-container');
            paletteContainer.appendChild(clickableContainer);
            
            // Add data attribute to store the palette index
            clickableContainer.dataset.paletteIndex = i;
            clickableContainer.dataset.collection = collection;
            
            // Add preview image container
            const previewContainer = document.createElement('div');
            previewContainer.classList.add('palette-preview-container');
            clickableContainer.appendChild(previewContainer);
            
            // Create small preview canvas
            const previewCanvas = document.createElement('canvas');
            previewCanvas.width = 200;
            previewCanvas.height = 200;
            previewCanvas.classList.add('palette-preview-canvas');
            previewContainer.appendChild(previewCanvas);
            
            // Display the representative colors underneath the preview
            const swatchContainer = document.createElement('div');
            swatchContainer.classList.add('swatch-container');
            clickableContainer.appendChild(swatchContainer);
            
            // Prepare display colors - ONE FROM EACH COLOR FAMILY
            const displayColors = prepareDisplayColors(paletteColors);
            
            // Display color swatches under the preview
            displayColors.forEach((color, idx) => {
                const swatch = document.createElement('div');
                swatch.classList.add('color-swatch');
                swatch.style.backgroundColor = `rgb(${color.join(',')})`;
                
                // Updated tooltip with HEX value instead of RGB
                const hexValue = rgbToHex(color[0], color[1], color[2]);
                swatch.title = ` ${hexValue}`;
                
                if (collection === 'ss') {
                    swatch.classList.add('ss-swatch');
                } else if (collection === 'aw') {
                    swatch.classList.add('aw-swatch');
                }
                
                swatchContainer.appendChild(swatch);
            });
            
            // Click handler to use the FULL palette
            clickableContainer.addEventListener('click', function() {
                const paletteIndex = parseInt(this.dataset.paletteIndex, 10);
                const collectionName = this.dataset.collection;
                
                // Get the FULL palette from storage
                const fullPalette = window[`${collectionName}PaletteColors`] && 
                                  window[`${collectionName}PaletteColors`][paletteIndex];
                
                // Call processPallet with the FULL palette from storage
                if (typeof window.processPallet === 'function' && fullPalette && fullPalette.length > 0) {
                    window.processPallet(null, totalLayers, null, 0, null, fullPalette, paletteIndex, collectionName);
                }
            });
            
            // Add "Show All" button
            const showAllButton = document.createElement('div');
            showAllButton.classList.add('show-all-colors-btn');
            showAllButton.innerHTML = '+';
            showAllButton.title = 'Show all colors in palette';
            clickableContainer.appendChild(showAllButton);
            
            // Add event listener to show all colors in a modal
            showAllButton.addEventListener('click', function(e) {
                e.stopPropagation(); // Prevent triggering the parent container's click
                
                const fullPalette = window[`${collection}PaletteColors`][i];
                if (!fullPalette || fullPalette.length === 0) {
                    return;
                }
                
                showFullPaletteModal(fullPalette, collection, i);
            });
            
            // Store the palette info for preview generation using STORED palette
            paletteContainers.push({
                index: i,
                canvas: previewCanvas,
                colors: paletteColors // Use the stored palette colors
            });
        }
        
        // Generate previews one by one with small delays between each to avoid overloading the browser
        for (let i = 0; i < paletteContainers.length; i++) {
            const item = paletteContainers[i];
            
            // Use setTimeout to stagger the preview generation
            setTimeout(() => {
                generateAndShowPreview(item.canvas, item.colors, item.index, collection);
            }, i * 50); // Small delay between each preview start (50ms per palette)
        }
    } else {
        // Multi-layer logic - ALSO NEEDS THE SAME FIX
        const paletteContainer = document.getElementById(`${prefix}colorPalette_${layerIndex}`);
        if (!paletteContainer) return;
        
        // Initialize storage first
        window[`${collection}PaletteColors`] = window[`${collection}PaletteColors`] || {};
        window[`${collection}PaletteHueShifted`] = window[`${collection}PaletteHueShifted`] || {};
        
        // FIXED: Check if palette is already stored, if not generate and store it
        let paletteColors;
        if (window[`${collection}PaletteColors`][layerIndex]) {
            // Use existing stored palette
            paletteColors = window[`${collection}PaletteColors`][layerIndex];
        } else {
            // Generate and store new palette
            if (layerIndex < 5) {
                // Use hue shifting for first 5 layers
                const hueShiftedPalettes = generateHueShiftedPalettes(validatedColors, collection);
                paletteColors = hueShiftedPalettes[layerIndex] || [...validatedColors];
                
                // Mark this as hue-shifted
                window[`${collection}PaletteHueShifted`][layerIndex] = true;
            } else {
                // Use family replacement for layers 5+
                const diversePalettes = generateDiversePalettes(validatedColors);
                paletteColors = diversePalettes[layerIndex % diversePalettes.length] || [...validatedColors];
            }
            
            // Store the palette
            window[`${collection}PaletteColors`][layerIndex] = [...paletteColors];
        }
        
        // ... rest of multi-layer logic remains the same ...
    }
    
    setTimeout(() => {
        syncFavoriteStarsWithAllCategories();
    }, 500);
}