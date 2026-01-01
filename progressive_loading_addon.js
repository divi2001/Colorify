// ============================================
// PROGRESSIVE LOADING ADDON
// This file adds progressive loading to existing displayColorPalette
// ============================================

// Configuration
const PALETTES_PER_BATCH = 5;
const TOTAL_PALETTES = 35;
const PREVIEW_DELAY = 200; // ms between preview requests

// Track loading state
window.paletteLoadingState = {
    trending: { loaded: 5, total: TOTAL_PALETTES, isLoading: false },
    ss: { loaded: 5, total: TOTAL_PALETTES, isLoading: false },
    aw: { loaded: 5, total: TOTAL_PALETTES, isLoading: false }
};

// Preview generation queue
window.previewQueue = [];
window.isProcessingQueue = false;

// ============================================
// INTERCEPT AND MODIFY displayColorPalette
// ============================================
(function() {
    // Store original function
    const originalDisplayColorPalette = window.displayColorPalette;
    
    // Override with progressive loading version
    window.displayColorPalette = async function(layerIndex, colors, collection = 'trending', maxVisibleColors = 6, totalLayers = 1) {
        // For single layer mode, only create initial 5 palettes
        if (totalLayers === 1) {
            // Call original function but modify the loop to only create 5
            await originalDisplayColorPalette.call(this, layerIndex, colors, collection, maxVisibleColors, totalLayers);
            
            // Hide palettes 5-34 initially
            const prefix = collection + '_';
            for (let i = 5; i < 35; i++) {
                const container = document.getElementById(`${prefix}palette_container_${i}`);
                if (container) {
                    container.style.display = 'none';
                }
            }
            
            // Show load more button
            const loadMoreContainer = document.getElementById(`${collection}-load-more-container`);
            if (loadMoreContainer) {
                loadMoreContainer.style.display = 'block';
            }
            
            // Update counter
            updateLoadMoreButton(collection);
        } else {
            // For multi-layer, call original function as-is
            await originalDisplayColorPalette.call(this, layerIndex, colors, collection, maxVisibleColors, totalLayers);
        }
    };
})();

// ============================================
// LOAD MORE PALETTES FUNCTION
// ============================================
async function loadMorePalettes(collection) {
    const state = window.paletteLoadingState[collection];
    
    if (state.isLoading || state.loaded >= state.total) {
        return;
    }
    
    state.isLoading = true;
    const btn = document.getElementById(`${collection}-load-more-btn`);
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Loading...';
    }
    
    const startIndex = state.loaded;
    const endIndex = Math.min(startIndex + PALETTES_PER_BATCH, state.total);
    const prefix = collection + '_';
    
    // Show the next batch of palettes
    for (let i = startIndex; i < endIndex; i++) {
        const container = document.getElementById(`${prefix}palette_container_${i}`);
        if (container) {
            container.style.display = 'flex';
            
            // Queue preview generation one at a time
            const canvas = container.querySelector('.palette-preview-canvas');
            const paletteColors = window[`${collection}PaletteColors`][i];
            
            if (canvas && paletteColors) {
                queuePreviewGeneration(canvas, paletteColors, i, collection);
            }
        }
        
        // Small delay between showing each palette
        await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    // Update loaded count
    state.loaded = endIndex;
    updateLoadMoreButton(collection);
    
    state.isLoading = false;
    
    if (btn && state.loaded < state.total) {
        btn.disabled = false;
        btn.textContent = 'Load More Palettes';
    }
}

// ============================================
// UPDATE LOAD MORE BUTTON
// ============================================
function updateLoadMoreButton(collection) {
    const state = window.paletteLoadingState[collection];
    const counter = document.getElementById(`${collection}-loaded-count`);
    const container = document.getElementById(`${collection}-load-more-container`);
    
    if (counter) {
        counter.textContent = state.loaded;
    }
    
    if (state.loaded >= state.total) {
        if (container) {
            container.style.display = 'none';
        }
    }
}

// ============================================
// QUEUE PREVIEW GENERATION (ONE AT A TIME)
// ============================================
function queuePreviewGeneration(canvas, colors, index, collection) {
    window.previewQueue.push({
        canvas: canvas,
        colors: colors,
        index: index,
        collection: collection
    });
    
    if (!window.isProcessingQueue) {
        processPreviewQueue();
    }
}

// ============================================
// PROCESS PREVIEW QUEUE SEQUENTIALLY
// ============================================
async function processPreviewQueue() {
    if (window.previewQueue.length === 0) {
        window.isProcessingQueue = false;
        return;
    }
    
    window.isProcessingQueue = true;
    const item = window.previewQueue.shift();
    
    try {
        // Call the existing generateAndShowPreview function
        if (typeof generateAndShowPreview === 'function') {
            await generateAndShowPreview(item.canvas, item.colors, item.index, item.collection);
        }
    } catch (error) {
        console.error('Preview generation error:', error);
    }
    
    // Wait before processing next
    await new Promise(resolve => setTimeout(resolve, PREVIEW_DELAY));
    
    // Process next in queue
    processPreviewQueue();
}

// ============================================
// INITIALIZE ON PAGE LOAD
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Progressive loading addon initialized');
    
    // Set initial state
    ['trending', 'ss', 'aw'].forEach(collection => {
        const state = window.paletteLoadingState[collection];
        state.loaded = 5;
        updateLoadMoreButton(collection);
    });
});
