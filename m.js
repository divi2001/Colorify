function generateBaseColorPalettes(baseColor, backgroundColorIndex = 0) {
  // Conversion utilities
  function rgbToHex(r, g, b) {
    return '#' + [r, g, b].map(x => {
      const hex = x.toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    }).join('');
  }

  function rgbToHsl(r, g, b) {
    r /= 255;
    g /= 255;
    b /= 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
      h = s = 0;
    } else {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        case b: h = (r - g) / d + 4; break;
      }
      h /= 6;
    }

    return [h * 360, s * 100, l * 100];
  }

  function hslToRgb(h, s, l) {
    h /= 360;
    s /= 100;
    l /= 100;

    let r, g, b;

    if (s === 0) {
      r = g = b = l;
    } else {
      const hue2rgb = (p, q, t) => {
        if (t < 0) t += 1;
        if (t > 1) t -= 1;
        if (t < 1/6) return p + (q - p) * 6 * t;
        if (t < 1/2) return q;
        if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
        return p;
      };

      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;

      r = hue2rgb(p, q, h + 1/3);
      g = hue2rgb(p, q, h);
      b = hue2rgb(p, q, h - 1/3);
    }

    return [
      Math.round(r * 255),
      Math.round(g * 255),
      Math.round(b * 255)
    ];
  }

  function randomInRange(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  // Get the original colors from various sources
  let distinctColors = [];
  let originalBackgroundColor = null;

  try {
    // Get colors from various sources (unchanged)
    if (window.originalColors && Array.isArray(window.originalColors) && window.originalColors.length > 0) {
      console.log("Using originalColors with background index:", backgroundColorIndex);
      distinctColors = [...window.originalColors];
      
      if (backgroundColorIndex >= 0 && backgroundColorIndex < distinctColors.length) {
        originalBackgroundColor = [...distinctColors[backgroundColorIndex]];
      }
    } 
    else if (localStorage.getItem('distinctColorsArrayColorPallet')) {
      try {
        const storedColorsString = localStorage.getItem('distinctColorsArrayColorPallet');
        const storedColors = JSON.parse(storedColorsString);

        if (Array.isArray(storedColors) && storedColors.length > 0) {
          distinctColors = storedColors.filter(color =>
            Array.isArray(color) &&
            color.length === 3 &&
            color.every(val => typeof val === 'number' && !isNaN(val))
          );
        }
      } catch (parseError) {
        console.error("Error parsing colors from localStorage:", parseError);
      }
    }
    else if (window.distinctColorsArrayColorPallet &&
             Array.isArray(window.distinctColorsArrayColorPallet) &&
             window.distinctColorsArrayColorPallet.length > 0) {

      distinctColors = window.distinctColorsArrayColorPallet.filter(color =>
        Array.isArray(color) &&
        color.length === 3 &&
        color.every(val => typeof val === 'number' && !isNaN(val))
      );
    }

    if (distinctColors.length === 0) {
      distinctColors = [
        [230, 140, 30],  // Orange
        [50, 80, 200],   // Blue
        [60, 180, 70],   // Green
        [240, 220, 40],  // Yellow
        [150, 60, 180],  // Purple
        [255, 0, 255]    // Magenta
      ];
    }
  } catch (e) {
    console.error("Error retrieving distinct colors:", e);
    distinctColors = [
      [230, 140, 30], [50, 80, 200], [60, 180, 70],
      [240, 220, 40], [150, 60, 180], [255, 0, 255]
    ];
  }

  // Get the base color's HSL values
  const baseHsl = rgbToHsl(...baseColor);
  
  try {
    // NEW: Get harmony scheme from the parameters or use default
    const harmonyScheme = baseColor.harmonyScheme || 'normal';
    const shadeType = baseColor.shadeType || 'regular';
    
    // STEP 1: Create base color variants based on requested harmony scheme
    let baseColorVariants = [];
    
    // Generate colors based on harmony scheme
    function generateHarmonyColors(baseHsl, scheme) {
      const hue = baseHsl[0];
      const saturation = baseHsl[1];
      const lightness = baseHsl[2];
      const colors = [];
      
      switch(scheme) {
        case 'monochromatic':
          // Same hue, different saturation and lightness
          colors.push([hue, saturation, lightness]); // Base color
          colors.push([hue, Math.min(100, saturation * 0.7), lightness]); // Less saturated
          colors.push([hue, Math.min(100, saturation * 1.3), lightness]); // More saturated
          colors.push([hue, saturation, Math.max(10, lightness - 20)]); // Darker
          colors.push([hue, saturation, Math.min(90, lightness + 20)]); // Lighter
          colors.push([hue, Math.min(100, saturation * 0.8), Math.max(10, lightness - 15)]); // Less saturated & darker
          break;
          
        case 'analogous':
          // Adjacent colors on the color wheel (base hue ± 30°)
          colors.push([hue, saturation, lightness]); // Base color
          colors.push([(hue + 30) % 360, saturation, lightness]); // +30 degrees
          colors.push([(hue + 60) % 360, saturation, lightness]); // +60 degrees
          colors.push([(hue - 30 + 360) % 360, saturation, lightness]); // -30 degrees
          colors.push([(hue - 60 + 360) % 360, saturation, lightness]); // -60 degrees
          colors.push([hue, saturation, Math.max(20, lightness - 15)]); // Base but darker
          break;
          
        case 'complementary':
          // Base color and its complement (opposite on the color wheel)
          colors.push([hue, saturation, lightness]); // Base color
          colors.push([(hue + 180) % 360, saturation, lightness]); // Complementary
          colors.push([hue, Math.min(100, saturation * 0.8), Math.max(15, lightness - 20)]); // Darker base
          colors.push([(hue + 180) % 360, Math.min(100, saturation * 0.8), Math.max(15, lightness - 20)]); // Darker complement
          colors.push([hue, Math.min(100, saturation * 0.9), Math.min(90, lightness + 15)]); // Lighter base
          colors.push([(hue + 180) % 360, Math.min(100, saturation * 0.9), Math.min(90, lightness + 15)]); // Lighter complement
          break;
          
        case 'splitComplementary':
          // Base color and colors on both sides of its complement (±30° from complement)
          colors.push([hue, saturation, lightness]); // Base color
          colors.push([(hue + 150) % 360, saturation, lightness]); // Split complement 1
          colors.push([(hue + 210) % 360, saturation, lightness]); // Split complement 2
          colors.push([hue, Math.min(100, saturation * 0.7), Math.max(20, lightness - 10)]); // Darker base
          colors.push([(hue + 150) % 360, Math.min(100, saturation * 0.8), Math.min(90, lightness + 10)]); // Lighter split 1
          colors.push([(hue + 210) % 360, Math.min(100, saturation * 0.9), Math.max(20, lightness - 10)]); // Darker split 2
          break;
          
        case 'triadic':
          // Three colors equally spaced on the color wheel (120° apart)
          colors.push([hue, saturation, lightness]); // Base color
          colors.push([(hue + 120) % 360, saturation, lightness]); // +120 degrees
          colors.push([(hue + 240) % 360, saturation, lightness]); // +240 degrees
          colors.push([hue, Math.min(100, saturation * 0.8), Math.max(20, lightness - 15)]); // Darker base
          colors.push([(hue + 120) % 360, Math.min(100, saturation * 0.9), Math.min(90, lightness + 10)]); // Lighter +120
          colors.push([(hue + 240) % 360, Math.min(100, saturation * 0.7), Math.max(30, lightness - 5)]); // Slightly darker +240
          break;
          
        case 'tetradic':
          // Four colors arranged in two complementary pairs
          colors.push([hue, saturation, lightness]); // Base color
          colors.push([(hue + 90) % 360, saturation, lightness]); // +90 degrees
          colors.push([(hue + 180) % 360, saturation, lightness]); // +180 degrees
          colors.push([(hue + 270) % 360, saturation, lightness]); // +270 degrees
          colors.push([hue, Math.min(100, saturation * 0.8), Math.max(20, lightness - 10)]); // Darker base
          colors.push([(hue + 180) % 360, Math.min(100, saturation * 0.8), Math.min(90, lightness + 10)]); // Lighter complement
          break;
          
        case 'square':
          // Four colors evenly spaced around the color wheel (90° apart)
          colors.push([hue, saturation, lightness]); // Base color
          colors.push([(hue + 90) % 360, saturation, lightness]); // +90 degrees
          colors.push([(hue + 180) % 360, saturation, lightness]); // +180 degrees
          colors.push([(hue + 270) % 360, saturation, lightness]); // +270 degrees
          colors.push([hue, Math.min(100, saturation * 0.9), Math.min(90, lightness + 15)]); // Lighter base
          colors.push([(hue + 180) % 360, Math.min(100, saturation * 0.7), Math.max(20, lightness - 15)]); // Darker complement
          break;
          
        case 'normal':
        default:
          // Generate a normal palette with varied colors
          colors.push([hue, saturation, lightness]); // Base color
          colors.push([(hue + 30) % 360, saturation, lightness]); // Slight shift
          colors.push([(hue + 60) % 360, saturation, lightness]); // More shift
          colors.push([(hue + 180) % 360, saturation, lightness]); // Complement
          colors.push([hue, Math.min(100, saturation * 0.7), Math.max(20, lightness - 15)]); // Darker base
          colors.push([hue, Math.min(100, saturation * 0.8), Math.min(90, lightness + 15)]); // Lighter base
          break;
      }
      
      return colors;
    }
    
    // Generate base harmony colors in HSL
    const harmonyColorsHSL = generateHarmonyColors(baseHsl, harmonyScheme);
    
    // Adjust for shade type (faint, regular, dark)
    for (let i = 0; i < harmonyColorsHSL.length; i++) {
      const colorHSL = harmonyColorsHSL[i];
      let adjustedHSL = [...colorHSL];
      
      // Adjust lightness and saturation based on shade type
      if (shadeType === 'faint') {
        // For faint: increase lightness, reduce saturation slightly
        adjustedHSL[1] = Math.max(10, colorHSL[1] * 0.7); // Reduce saturation
        adjustedHSL[2] = Math.min(95, 70 + (i % 25)); // 70-95% lightness
      } 
      else if (shadeType === 'dark') {
        // For dark: decrease lightness, possibly increase saturation slightly
        adjustedHSL[1] = Math.min(100, colorHSL[1] * 1.1); // Slightly increase saturation
        adjustedHSL[2] = Math.max(10, 35 - (i % 25)); // 10-35% lightness
      }
      else {
        // For regular: keep similar to original but ensure good range
        adjustedHSL[2] = Math.min(75, Math.max(30, colorHSL[2]));
      }
      
      // Convert HSL to RGB and add to variants
      const variantRGB = hslToRgb(...adjustedHSL);
      
      baseColorVariants.push({
        color: variantRGB,
        category: shadeType,
        harmonyScheme: harmonyScheme,
        hsl: adjustedHSL,
        index: i
      });
    }
    
    // STEP 2: Create distinctly different palettes using these variants
    const basePalettes = [];
    
    // Generate 12 palettes for each combination of shade and harmony
    const totalPalettes = 12;
    
    for (let paletteIndex = 0; paletteIndex < totalPalettes; paletteIndex++) {
      // For each palette, pick a variant as the base
      const variantIndex = paletteIndex % baseColorVariants.length;
      const variant = baseColorVariants[variantIndex];
      
      // Create a working copy of distinctColors
      let workingColors = [...distinctColors];
      
      // Replace the background color with the current base color variant
      if (backgroundColorIndex >= 0 && backgroundColorIndex < workingColors.length) {
        workingColors[backgroundColorIndex] = variant.color;
      }
      
      // Convert all colors to HSL for easier manipulation
      const workingColorsHSL = workingColors.map(color => rgbToHsl(...color));
      
      // Adjust the other colors in the palette to coordinate with the base variant
      let newPalette = [];
      
      for (let j = 0; j < workingColors.length; j++) {
        if (j === backgroundColorIndex) {
          // Use the exact variant color for the background position
          newPalette.push([...variant.color]);
          continue;
        }
        
        // For other colors, create coordinating colors based on harmony scheme
        // This helps maintain color relationships
        const originalBgHSL = workingColorsHSL[backgroundColorIndex];
        
        // Get harmony colors for this palette
        const harmonyColors = generateHarmonyColors(variant.hsl, harmonyScheme);
        
        // Pick a harmony color based on position in the palette
        const harmonyIndex = j % harmonyColors.length;
        let newHSL = [...harmonyColors[harmonyIndex]];
        
        // Apply small variations for diversity
        newHSL[0] = (newHSL[0] + randomInRange(-5, 5) + 360) % 360;
        newHSL[1] = Math.min(100, Math.max(5, newHSL[1] + randomInRange(-5, 5)));
        newHSL[2] = Math.min(95, Math.max(5, newHSL[2] + randomInRange(-5, 5)));
        
        // Apply shade type adjustments
        if (shadeType === 'faint') {
          newHSL[2] = Math.max(newHSL[2], 70); // Ensure lightness is at least 70%
        } else if (shadeType === 'dark') {
          newHSL[2] = Math.min(newHSL[2], 40); // Ensure lightness is at most 40%
        }
        
        const newColor = hslToRgb(...newHSL);
        newPalette.push(newColor);
      }
      
      // Ensure we have enough colors (at least 6)
      while (newPalette.length < 6) {
        // Generate additional coordinating colors based on harmony
        const harmonyColors = generateHarmonyColors(variant.hsl, harmonyScheme);
        const harmonyIndex = (newPalette.length) % harmonyColors.length;
        
        let newHSL = [...harmonyColors[harmonyIndex]];
        
        // Apply variations
        newHSL[0] = (newHSL[0] + randomInRange(-10, 10) + 360) % 360;
        newHSL[1] = Math.min(100, Math.max(5, newHSL[1] + randomInRange(-10, 10)));
        newHSL[2] = Math.min(95, Math.max(5, newHSL[2] + randomInRange(-10, 10)));
        
        // Apply shade type adjustments
        if (shadeType === 'faint') {
          newHSL[2] = Math.max(newHSL[2], 70); // Ensure lightness is at least 70%
        } else if (shadeType === 'dark') {
          newHSL[2] = Math.min(newHSL[2], 40); // Ensure lightness is at most 40%
        }
        
        const additionalColor = hslToRgb(...newHSL);
        newPalette.push(additionalColor);
      }
      
      // Add the palette info with both category and harmony scheme
      Object.defineProperty(newPalette, 'info', {
        value: { 
          category: shadeType,
          harmonyScheme: harmonyScheme,
          variantIndex: variant.index
        },
        enumerable: false
      });
      
      basePalettes.push(newPalette);
    }
    
    return basePalettes;
    
  } catch (e) {
    console.error("Error generating base color variants:", e);
    
    // Provide fallback palettes with more variety
    const basePalettes = [];
    const fallbackShadeType = baseColor.shadeType || 'regular';
    const fallbackHarmonyScheme = baseColor.harmonyScheme || 'normal';
    
    for (let i = 0; i < 12; i++) {
      let fallbackPalette = [];
      
      // Create a palette with the base color in the background position
      for (let j = 0; j < 6; j++) {
        if (j === backgroundColorIndex) {
          // Adjust the base color based on category with more variety
          const baseHsl = rgbToHsl(...baseColor);
          let adjustedHsl = [...baseHsl];
          
          if (fallbackShadeType === "faint") {
            // Create distinctly different faint variants
            adjustedHsl[1] = Math.max(10, baseHsl[1] * (0.5 + (i * 0.15)));
            adjustedHsl[2] = Math.min(95, 70 + (i * 8));
          } 
          else if (fallbackShadeType === "dark") {
            // Create distinctly different dark variants
            adjustedHsl[1] = Math.min(100, baseHsl[1] * (1.0 + (i * 0.1)));
            adjustedHsl[2] = Math.max(5, 35 - (i * 8));
          }
          else {
            // Create distinctly different regular variants
            const variation = (i) * 5;
            adjustedHsl[1] = Math.min(100, Math.max(10, baseHsl[1] + variation));
            adjustedHsl[2] = Math.min(80, Math.max(30, baseHsl[2] + variation));
          }
          
          fallbackPalette.push(hslToRgb(...adjustedHsl));
        } else {
          // Add complementary colors with more variety
          let hueOffset;
          
          // Determine hue offset based on harmony scheme
          if (fallbackHarmonyScheme === 'monochromatic') {
            hueOffset = 0; // Same hue
          } else if (fallbackHarmonyScheme === 'analogous') {
            hueOffset = 30 * (j % 4) - 60; // -60, -30, 0, 30, 60 degrees
          } else if (fallbackHarmonyScheme === 'complementary') {
            hueOffset = j % 2 === 0 ? 0 : 180; // Either same or opposite
          } else if (fallbackHarmonyScheme === 'splitComplementary') {
            hueOffset = j % 3 === 0 ? 0 : (j % 3 === 1 ? 150 : 210); // Base, +150, +210
          } else if (fallbackHarmonyScheme === 'triadic') {
            hueOffset = 120 * (j % 3); // 0, 120, 240 degrees
          } else if (fallbackHarmonyScheme === 'tetradic' || fallbackHarmonyScheme === 'square') {
            hueOffset = 90 * (j % 4); // 0, 90, 180, 270 degrees
          } else {
            // Normal/default
            hueOffset = 60 * j; // 0, 60, 120, 180, 240, 300 degrees
          }
          
          const baseHsl = rgbToHsl(...baseColor);
          const hue = (baseHsl[0] + hueOffset + (i * 5)) % 360;
          
          let sat, light;
          if (fallbackShadeType === "faint") {
            sat = 30 + (i * 5);
            light = 80 - (i * 3);
          } else if (fallbackShadeType === "dark") {
            sat = 70 + (i * 3);
            light = 25 - (i * 2);
          } else {
            sat = 50 + (i * 3);
            light = 50 + ((i) * 2);
          }
          
          sat = Math.min(100, Math.max(0, sat));
          light = Math.min(100, Math.max(0, light));
          
          fallbackPalette.push(hslToRgb(hue, sat, light));
        }
      }
      
      // Add the palette info
      Object.defineProperty(fallbackPalette, 'info', {
        value: { 
          category: fallbackShadeType,
          harmonyScheme: fallbackHarmonyScheme
        },
        enumerable: false
      });
      
      basePalettes.push(fallbackPalette);
    }
    
    return basePalettes;
  }
}

// Modified selectBaseColor function with shade and harmony filters
async function selectBaseColor(color) {
  try {
    // Invalidate the cache when a new base color is selected
    if (window.palettePreviewCache && window.palettePreviewCache['base']) {
      // Clear all cached previews for base palettes
      window.palettePreviewCache['base'] = {};
    }
    
    // Remove any existing filter container
    const filterContainer = document.querySelector('.base-color-filters');
    if (filterContainer) {
      filterContainer.remove();
    }
    
    // Get color name
    const colorName = getColorName(color);
    
    // RGB to HEX conversion function
    function rgbToHex(r, g, b) {
      return '#' + [r, g, b].map(x => {
        const hex = x.toString(16);
        return hex.length === 1 ? '0' + hex : hex;
      }).join('');
    }
    
    // Check for ML label in the layers
    let mlLabel = null;
    const layerElement = document.querySelector('.layer[data-ml-label]');
    if (layerElement) {
      mlLabel = parseInt(layerElement.dataset.mlLabel, 10);
      console.log("Found ML label:", mlLabel);
    }
    
    // Process based on ML label
    if (mlLabel !== null) {
      if (mlLabel === 1) {
        // ML label 1: Image doesn't support base color selection
        alert("This image doesn't support base color selection based on our analysis. The image structure may be too complex for effective color mapping.");
        // Reset the view and return early
        resetBaseColorView();
        return;
      } 
      else if (mlLabel === 2) {
        // ML label 2: Image has complicated colors, warn user
        const shouldContinue = confirm("This image has a complicated color structure. Base color selection may produce unexpected results. Would you like to proceed anyway?");
        
        if (!shouldContinue) {
          resetBaseColorView();
          return; // User chose not to continue
        }
        // Otherwise continue with normal flow...
      }
      // For label 0, proceed normally without any warnings
    }
    
    // FIRST: Ensure window.originalColors is set from distinctColorsArrayColorPallet
    if (!window.originalColors || !Array.isArray(window.originalColors) || window.originalColors.length === 0) {
      // Try to get colors from window variable
      if (window.distinctColorsArrayColorPallet && 
          Array.isArray(window.distinctColorsArrayColorPallet) && 
          window.distinctColorsArrayColorPallet.length > 0) {
        
        window.originalColors = [...window.distinctColorsArrayColorPallet];
        console.log("Set window.originalColors from window.distinctColorsArrayColorPallet:", window.originalColors);
      }
      // Or try localStorage if window variable isn't available
      else if (localStorage.getItem('distinctColorsArrayColorPallet')) {
        try {
          const colorsString = localStorage.getItem('distinctColorsArrayColorPallet');
          const parsedColors = JSON.parse(colorsString);
          
          if (Array.isArray(parsedColors) && parsedColors.length > 0) {
            window.originalColors = parsedColors;
            console.log("Set window.originalColors from localStorage:", window.originalColors);
          }
        } catch (e) {
          console.error("Error parsing distinctColorsArrayColorPallet from localStorage:", e);
        }
      }
      
      // Make sure the colors are valid RGB arrays
      if (window.originalColors) {
        window.originalColors = window.originalColors.filter(color => 
          Array.isArray(color) && 
          color.length === 3 && 
          color.every(component => typeof component === 'number' && !isNaN(component))
        );
      }
    }

    // Determine which color should be the background color
    let backgroundColorIndex = null; 
    
    // If we have original colors from an image, ask if user wants to select background
    if (window.originalColors && Array.isArray(window.originalColors) && window.originalColors.length > 0) {
      // Create a simple confirmation dialog
      const wantsToSelectBG = await new Promise(resolve => {
        // Create confirmation modal
        const confirmModal = document.createElement('div');
        confirmModal.className = 'bg-select-confirm-overlay';
        confirmModal.style.cssText = `
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background-color: rgba(0,0,0,0.7);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 9999;
        `;
        
        const confirmContent = document.createElement('div');
        confirmContent.className = 'bg-select-confirm-content';
        confirmContent.style.cssText = `
          background-color: white;
          border-radius: 8px;
          padding: 20px;
          max-width: 90%;
          width: 400px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.3);
          text-align: center;
        `;
        
        const confirmTitle = document.createElement('h4');
        confirmTitle.textContent = 'Background Color Selection';
        confirmTitle.style.marginBottom = '15px';
        
        const confirmText = document.createElement('p');
        confirmText.textContent = 'Would you like to choose which color from your image should be treated as the background color?';
        
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = `
          display: flex;
          justify-content: center;
          gap: 15px;
          margin-top: 20px;
        `;
        
        const yesButton = document.createElement('button');
        yesButton.textContent = 'Yes, select background';
        yesButton.style.cssText = `
          padding: 8px 16px;
          background-color: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        `;
        
        const noButton = document.createElement('button');
        noButton.textContent = 'No, use default';
        noButton.style.cssText = `
          padding: 8px 16px;
          border: 1px solid #ddd;
          background-color: white;
          border-radius: 4px;
          cursor: pointer;
        `;
        
        yesButton.addEventListener('click', () => {
          document.body.removeChild(confirmModal);
          resolve(true);
        });
        
        noButton.addEventListener('click', () => {
          document.body.removeChild(confirmModal);
          resolve(false);
        });
        
        buttonContainer.appendChild(noButton);
        buttonContainer.appendChild(yesButton);
        
        confirmContent.appendChild(confirmTitle);
        confirmContent.appendChild(confirmText);
        confirmContent.appendChild(buttonContainer);
        confirmModal.appendChild(confirmContent);
        
        document.body.appendChild(confirmModal);
      });

      console.log("Original colors available:", window.originalColors);
      console.log("Is array?", Array.isArray(window.originalColors));
      console.log("Length:", window.originalColors ? window.originalColors.length : 0);
      
      // If user wants to select background color, show the selector
      if (wantsToSelectBG) {
        console.log("Showing background color selector...");
        backgroundColorIndex = await showBackgroundColorSelector(color, window.originalColors);
        console.log(`User selected background color index: ${backgroundColorIndex}`);
      } else {
        // User didn't want to select, so find the best matching color as background
        // We'll look for the brightest color or closest to white as default background
        let maxBrightness = -1;
        window.originalColors.forEach((c, idx) => {
          // Simple brightness formula: (R+G+B)/3
          const brightness = (c[0] + c[1] + c[2]) / 3;
          if (brightness > maxBrightness) {
            maxBrightness = brightness;
            backgroundColorIndex = idx;
          }
        });
        console.log(`Using brightest color as background (index: ${backgroundColorIndex})`);
      }
    } else {
      console.log("No original colors available, using null for background index");
    }
    
    // Now that we have the background color index, proceed with UI updates
    
    // Hide the base colors grid
    const baseColorsGrid = document.querySelector('.base-colors-grid');
    baseColorsGrid.style.display = 'none';

    // Show the palettes section
    const basePalettesSection = document.querySelector('.base-palettes-section');
    if (basePalettesSection) {
      basePalettesSection.style.display = 'block';
    } else {
      console.error("Could not find .base-palettes-section element");
      return;
    }

    // Change the header text to indicate selected color
    const headerElement = document.querySelector('#baseColorContent h4');
    if (headerElement) {
      const hexColor = rgbToHex(color[0], color[1], color[2]);
      headerElement.textContent = `Palettes with ${colorName} (${hexColor})`;
    }

    // Add a back button next to the header if it doesn't exist
    if (!document.querySelector('.back-to-base-colors')) {
      const backButton = document.createElement('button');
      backButton.className = 'btn btn-sm btn-outline-secondary back-to-base-colors ms-2';
      backButton.innerHTML = '<i class="bi bi-arrow-left"></i> Back to Colors';
      backButton.onclick = resetBaseColorView;

      if (headerElement && headerElement.parentElement) {
        headerElement.parentElement.insertBefore(backButton, headerElement.nextSibling);
      }
    }

    // Store the selected base color
    window.selectedBaseColor = color;
    window.selectedBackgroundColorIndex = backgroundColorIndex;
    
    // Initialize palette storage
    window.basePaletteColors = {};
    window.basePaletteColors.shadeCategories = {};
    window.basePaletteColors.harmonySchemes = {};
    
    // Define harmony schemes
    const harmonySchemes = [
      'normal', 'monochromatic', 'analogous', 'complementary', 
      'splitComplementary', 'triadic', 'tetradic', 'square'
    ];
    
    // Define shade types
    const shadeTypes = ['faint', 'regular', 'dark'];
    
    // Generate palettes for each combination of harmony scheme and shade type
    let paletteIndex = 0;
    
    for (const harmonyScheme of harmonySchemes) {
      for (const shadeType of shadeTypes) {
        // Add harmony and shade info to the color object
        const colorWithInfo = [...color];
        colorWithInfo.harmonyScheme = harmonyScheme;
        colorWithInfo.shadeType = shadeType;
        
        // Generate 12 palettes for this combination
        const palettes = generateBaseColorPalettes(colorWithInfo, backgroundColorIndex);
        
        // Store generated palettes
        for (let i = 0; i < palettes.length; i++) {
          // Store the palette colors
          window.basePaletteColors[paletteIndex] = [...palettes[i]];
          
          // Store the category information
          window.basePaletteColors.shadeCategories[paletteIndex] = shadeType;
          window.basePaletteColors.harmonySchemes[paletteIndex] = harmonyScheme;
          
          paletteIndex++;
        }
      }
    }

    // Store in localStorage for persistence
    try {
      localStorage.setItem('basePaletteColors', JSON.stringify(window.basePaletteColors));
    } catch (e) {
      console.warn("Could not store basePaletteColors in localStorage:", e);
    }

    // Initialize preview cache if needed
    if (!window.palettePreviewCache) {
      window.palettePreviewCache = {};
    }
    if (!window.palettePreviewCache['base']) {
      window.palettePreviewCache['base'] = {};
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
    
    // Create the filters with dropdowns
    createBaseColorDropdownFilters(color);
    
    // Function to prepare display colors
    function prepareDisplayColors(colors) {
      try {
        // Make sure all colors are valid
        const validColors = colors.filter(color =>
          Array.isArray(color) &&
          color.length === 3 &&
          color.every(val => typeof val === 'number' && !isNaN(val))
        );

        // If no valid colors, return a basic palette
        if (validColors.length === 0) {
          console.warn("No valid colors for display, using basic palette");
          return [
            [...color], // Use selected color as first
            [0, 255, 0], [0, 0, 255],
            [255, 255, 0], [255, 0, 255], [0, 255, 255]
          ];
        }

        // Always preserve the first color (selected color)
        let displayColors = [validColors[0]];

        const FIXED_DISPLAY_COUNT = 6; // Fixed number for display consistency

        // If we have more than FIXED_DISPLAY_COUNT colors, use a subset for display
        if (validColors.length > FIXED_DISPLAY_COUNT) {
          // Select remaining display colors evenly distributed to maintain sequence
          const step = (validColors.length - 1) / (FIXED_DISPLAY_COUNT - 1);
          for (let i = 1; i < FIXED_DISPLAY_COUNT; i++) {
            const idx = Math.min(Math.floor(1 + (i - 1) * step), validColors.length - 1);
            displayColors.push(validColors[idx]);
          }
        } else if (validColors.length < FIXED_DISPLAY_COUNT) {
          // Add remaining colors
          for (let i = 1; i < validColors.length; i++) {
            displayColors.push(validColors[i]);
          }

          // If still not enough, duplicate some colors to reach FIXED_DISPLAY_COUNT
          while (displayColors.length < FIXED_DISPLAY_COUNT) {
            const idx = displayColors.length % validColors.length;
            displayColors.push([...validColors[idx]]);
          }
        } else {
          // We have exactly FIXED_DISPLAY_COUNT colors
          displayColors = [...validColors];
        }

        return displayColors;
      } catch (e) {
        console.error("Error preparing display colors:", e);
        // Return a fallback set of colors
        return [
          [...color], // Use selected color as first
          [0, 255, 0], [0, 0, 255],
          [255, 255, 0], [255, 0, 255], [0, 255, 255]
        ];
      }
    }

    // Function to display a modal with all colors in the palette
    function showFullPaletteModal(palette, collection, paletteIndex) {
      // Create and append modal elements if they don't exist
      let modal = document.getElementById('full-palette-modal');

      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'full-palette-modal';
        modal.classList.add('full-palette-modal');

        const modalContent = document.createElement('div');
        modalContent.classList.add('full-palette-modal-content');

        const closeBtn = document.createElement('span');
        closeBtn.classList.add('close-palette-modal');
        closeBtn.innerHTML = '&times;';

        const modalTitle = document.createElement('h3');
        modalTitle.classList.add('palette-modal-title');

        const colorsContainer = document.createElement('div');
        colorsContainer.classList.add('all-colors-container');

        modalContent.appendChild(closeBtn);
        modalContent.appendChild(modalTitle);
        modalContent.appendChild(colorsContainer);
        modal.appendChild(modalContent);

        document.body.appendChild(modal);

        // Add event listener to close button
        closeBtn.addEventListener('click', function() {
          modal.style.display = 'none';
        });

        // Close modal when clicking outside content
        window.addEventListener('click', function(event) {
          if (event.target === modal) {
            modal.style.display = 'none';
          }
        });
      }

      // Update modal content with current palette
      const modalTitle = modal.querySelector('.palette-modal-title');
      const colorsContainer = modal.querySelector('.all-colors-container');

      // Get palette category and harmony if available
      let category = "Regular";
      let harmony = "Normal";
      
      if (window.basePaletteColors) {
        if (window.basePaletteColors.shadeCategories && 
            window.basePaletteColors.shadeCategories[paletteIndex]) {
          category = window.basePaletteColors.shadeCategories[paletteIndex].charAt(0).toUpperCase() 
                  + window.basePaletteColors.shadeCategories[paletteIndex].slice(1);
        }
        
        if (window.basePaletteColors.harmonySchemes && 
            window.basePaletteColors.harmonySchemes[paletteIndex]) {
          // Format harmony scheme for display (e.g., "splitComplementary" -> "Split Complementary")
          const harmonyRaw = window.basePaletteColors.harmonySchemes[paletteIndex];
          harmony = harmonyRaw.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
          if (harmony === "Normal") harmony = "Standard";
        }
      }

      modalTitle.textContent = `Full Palette (${collection.toUpperCase()} #${paletteIndex+1} - ${category}, ${harmony})`;
      colorsContainer.innerHTML = '';

      // Add all colors to the modal
      palette.forEach((color, index) => {
        const colorBox = document.createElement('div');
        colorBox.classList.add('full-palette-color');
        colorBox.style.backgroundColor = `rgb(${color.join(',')})`;

        // Convert RGB to HEX for display
        const hexColor = rgbToHex(color[0], color[1], color[2]);

        // Add color information - using HEX code only
        const colorInfo = document.createElement('div');
        colorInfo.classList.add('color-info');
        colorInfo.textContent = `Color ${index+1}: ${hexColor}`;

        // Add tooltip with HEX code only
        colorBox.title = hexColor;

        colorBox.appendChild(colorInfo);
        colorsContainer.appendChild(colorBox);
      });

      // Show the modal
      modal.style.display = 'block';
    }
    
    // Function to generate a preview of the palette applied to the image
    async function generatePreview(previewCanvas, paletteColors, paletteIndex) {
      try {
        // Mark the container as not ready (ensure loading indicator shows)
        const container = previewCanvas.closest('.palette-clickable-container');
        if (container) {
          container.classList.remove('preview-ready');
        }
        
        // Check cache first - expanded cache check
        if (window.palettePreviewCache && 
            window.palettePreviewCache['base'] && 
            window.palettePreviewCache['base'][paletteIndex]) {
            
            // Use cached preview
            const cachedPreview = window.palettePreviewCache['base'][paletteIndex];
            const ctx = previewCanvas.getContext('2d', { willReadFrequently: true });
            
            // Clear with white background
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, previewCanvas.width, previewCanvas.height);
            
            return new Promise((resolve) => {
              const img = new Image();
              img.onload = () => {
                // Calculate proportional dimensions to maintain aspect ratio
                const scale = Math.min(
                    previewCanvas.width / img.width,
                    previewCanvas.height / img.height
                );
                
                const scaledWidth = img.width * scale;
                const scaledHeight = img.height * scale;
                
                // Center the image
                const x = (previewCanvas.width - scaledWidth) / 2;
                const y = (previewCanvas.height - scaledHeight) / 2;
                
                // Draw the image with proper aspect ratio
                ctx.drawImage(img, x, y, scaledWidth, scaledHeight);
                
                // Mark preview as ready to hide the loading indicator
                if (container) {
                  container.classList.add('preview-ready');
                }
                resolve();
              };
              img.onerror = () => {
                // Draw fallback and mark as ready
                drawFallbackPreview(previewCanvas);
                if (container) {
                  container.classList.add('preview-ready');
                }
                resolve();
              };
              img.src = cachedPreview;
            });
        }
            
            // No cache, create new preview
            // Get the original image
            const originalCanvas = document.getElementById('layer_canvas_1');
            
            if (!originalCanvas) {
              console.error('No original canvas found for preview');
              drawFallbackPreview(previewCanvas);
              if (container) {
                container.classList.add('preview-ready');
              }
              return;
            }
            
            // Clear the preview canvas with white background
            const ctx = previewCanvas.getContext('2d', { willReadFrequently: true });
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, previewCanvas.width, previewCanvas.height);
            
            // Calculate dimensions that maintain aspect ratio
            const originalAspect = originalCanvas.width / originalCanvas.height;
            let previewWidth, previewHeight, offsetX = 0, offsetY = 0;
            
            if (originalAspect > 1) {
              // Image is wider than tall
              previewWidth = previewCanvas.width;
              previewHeight = previewWidth / originalAspect;
              offsetY = (previewCanvas.height - previewHeight) / 2;
            } else {
              // Image is taller than wide
              previewHeight = previewCanvas.height;
              previewWidth = previewHeight * originalAspect;
              offsetX = (previewCanvas.width - previewWidth) / 2;
            }
            
            // Create a temporary canvas for the original image at preview size
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = previewWidth;
            tempCanvas.height = previewHeight;
            const tempCtx = tempCanvas.getContext('2d', { willReadFrequently: true });
            
            // Draw original image to temp canvas maintaining aspect ratio
            tempCtx.drawImage(originalCanvas, 0, 0, previewWidth, previewHeight);
            
            // Now get the temp canvas data for processing
            const imageData = tempCtx.getImageData(0, 0, previewWidth, previewHeight);
            
            // Find original colors from the image
            const originalColors = await getDistinctColors(imageData, 30, 50);
            
            if (!originalColors || originalColors.length === 0) {
              console.error('No original colors found for preview');
              // Still draw the original image with correct aspect ratio
              ctx.drawImage(tempCanvas, offsetX, offsetY);
              
              // Mark preview as ready
              if (container) {
                container.classList.add('preview-ready');
              }
              return;
            }
            
            // Create color mappings
            const colorMappings = [];
            
            // Special handling for background color
            if (backgroundColorIndex !== null && 
                backgroundColorIndex >= 0 && 
                backgroundColorIndex < originalColors.length) {
                
                // Map colors with special consideration for the background color
                for (let i = 0; i < originalColors.length; i++) {
                    if (i === backgroundColorIndex) {
                        // For the background color index, map to the selected base color (first in palette)
                        colorMappings.push({
                            originalColor: originalColors[i],
                            targetColor: paletteColors[0]
                        });
                    } else {
                        // For other colors, map to rest of palette
                        const targetIndex = (i < backgroundColorIndex) ? i + 1 : i;
                        const paletteIndex = targetIndex % paletteColors.length;
                        
                        colorMappings.push({
                            originalColor: originalColors[i],
                            targetColor: paletteColors[paletteIndex]
                        });
                    }
                }
            } else {
                // Regular mapping if no background color is specified
                for (let i = 0; i < Math.min(originalColors.length, paletteColors.length); i++) {
                    colorMappings.push({
                        originalColor: originalColors[i],
                        targetColor: paletteColors[i % paletteColors.length]
                    });
                }
            }
            
            // Use a simplified processor for the preview
            const colorProcessor = new ColorProcessor();
            const imageUrl = tempCanvas.toDataURL();
            
            // Process the preview
            const processedImageUrl = await colorProcessor.applyMultipleColorMappings(
                imageUrl,
                colorMappings
            );
            
            // Load the processed image back to the preview canvas
            return new Promise((resolve) => {
              const resultImg = new Image();
              resultImg.onload = () => {
                // Draw the processed image with the correct positioning
                ctx.drawImage(resultImg, offsetX, offsetY, previewWidth, previewHeight);
                
                // Cache the generated preview
                if (!window.palettePreviewCache) {
                    window.palettePreviewCache = {};
                }
                if (!window.palettePreviewCache['base']) {
                    window.palettePreviewCache['base'] = {};
                }
                window.palettePreviewCache['base'][paletteIndex] = previewCanvas.toDataURL();
                
                // Mark preview as ready to hide loading indicator
                if (container) {
                  container.classList.add('preview-ready');
                }
                resolve();
              };
              resultImg.onerror = () => {
                console.error("Error loading processed preview");
                drawFallbackPreview(previewCanvas);
                if (container) {
                  container.classList.add('preview-ready');
                }
                resolve();
              };
              resultImg.src = processedImageUrl;
            });
            
          } catch (error) {
            console.error("Error generating preview:", error);
            drawFallbackPreview(previewCanvas);
            const container = previewCanvas.closest('.palette-clickable-container');
            if (container) {
              container.classList.add('preview-ready');
            }
          }
        }

    // Helper function to draw fallback preview
    function drawFallbackPreview(canvas) {
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = 'white';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#f5f5f5';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#999';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.font = '14px sans-serif';
      ctx.fillText('Preview unavailable', canvas.width/2, canvas.height/2);
    }

    // Create or update palette containers - we need to ensure we have enough containers
    const palettesContainer = document.querySelector('.base-palettes-container');
    if (palettesContainer) {
      // Clear existing containers
      palettesContainer.innerHTML = '';

      // Calculate total palettes (all combinations of harmonies × shades × 12 palettes each)
      const TOTAL_PALETTES = harmonySchemes.length * shadeTypes.length * 12;
      
      // Create containers for all our palettes
      for (let i = 0; i < TOTAL_PALETTES; i++) {
        const paletteRow = document.createElement('div');
        paletteRow.className = 'row mb-4 palette-row';
        
        // Add data attributes for shade category and harmony scheme if available
        if (window.basePaletteColors) {
          if (window.basePaletteColors.shadeCategories && 
              window.basePaletteColors.shadeCategories[i]) {
            paletteRow.dataset.shadeCategory = window.basePaletteColors.shadeCategories[i];
          }
          
          if (window.basePaletteColors.harmonySchemes && 
              window.basePaletteColors.harmonySchemes[i]) {
            paletteRow.dataset.harmonyScheme = window.basePaletteColors.harmonySchemes[i];
          }
        }
        
        const paletteCol = document.createElement('div');
        paletteCol.className = 'col-12';
        paletteRow.appendChild(paletteCol);
        
        const paletteCard = document.createElement('div');
        paletteCard.className = 'card shadow-sm h-100';
        paletteCol.appendChild(paletteCard);
        
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';
        paletteCard.appendChild(cardBody);
        
        const paletteContainer = document.createElement('div');
        paletteContainer.id = `base_colorPalette_${i}`;
        paletteContainer.className = 'color-palette-container';
        cardBody.appendChild(paletteContainer);
        
        const paletteNumber = document.createElement('div');
        paletteNumber.className = 'palette-number';
        paletteNumber.textContent = `${i + 1}`;
        cardBody.appendChild(paletteNumber);
        
        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'btn-group w-100 mt-2';
        buttonsContainer.setAttribute('role', 'group');
        cardBody.appendChild(buttonsContainer);
        
        const shuffleButton = document.createElement('button');
        shuffleButton.id = `base_shufflePalette_${i}`;
        shuffleButton.className = 'btn btn-outline-secondary btn-sm';
        shuffleButton.innerHTML = '<i class="bi bi-shuffle"></i> Shuffle';
        shuffleButton.type = 'button';
        buttonsContainer.appendChild(shuffleButton);
        
        const applyButton = document.createElement('button');
        applyButton.id = `base_applyButton_${i}`;
        applyButton.className = 'btn btn-primary btn-sm';
        applyButton.innerHTML = '<i class="bi bi-check2-circle"></i> Apply';
        applyButton.type = 'button';
        buttonsContainer.appendChild(applyButton);
        
        palettesContainer.appendChild(paletteRow);
      }
    }

    // Display the generated palettes with previews
    for (let i = 0; i < Object.keys(window.basePaletteColors).length; i++) {
      if (i === 'shadeCategories' || i === 'harmonySchemes') continue;
      
      const paletteContainer = document.getElementById(`base_colorPalette_${i}`);
      if (!paletteContainer) continue;

      paletteContainer.innerHTML = '';

      // Get the generated palette
      const paletteColors = window.basePaletteColors[i];
      if (!paletteColors) continue;

      // Create container for the palette that will be clickable as a whole
      const clickableContainer = document.createElement('div');
      clickableContainer.classList.add('palette-clickable-container');
      paletteContainer.appendChild(clickableContainer);

      // Add data attribute to store the palette index
      clickableContainer.dataset.paletteIndex = i;
      clickableContainer.dataset.collection = 'base';
      
      // Get and store shade category and harmony scheme
      let shadeCategory = 'regular';
      let harmonyScheme = 'normal';
      
      if (window.basePaletteColors.shadeCategories && window.basePaletteColors.shadeCategories[i]) {
        shadeCategory = window.basePaletteColors.shadeCategories[i];
        clickableContainer.dataset.shadeCategory = shadeCategory;
      }
      
      if (window.basePaletteColors.harmonySchemes && window.basePaletteColors.harmonySchemes[i]) {
        harmonyScheme = window.basePaletteColors.harmonySchemes[i];
        clickableContainer.dataset.harmonyScheme = harmonyScheme;
      }
      
      // Add shade tag - visual indicator of palette type
      const shadeTags = document.createElement('div');
      shadeTags.className = 'scheme-tags';
      
      // Add shade tag
      const shadeTag = document.createElement('span');
      shadeTag.className = 'shade-tag';
      shadeTag.textContent = shadeCategory.charAt(0).toUpperCase() + shadeCategory.slice(1);
      shadeTags.appendChild(shadeTag);
      
      // Add harmony tag
      const harmonyTag = document.createElement('span');
      harmonyTag.className = 'harmony-tag';
      
      // Format harmony scheme for display
      let harmonyDisplay = harmonyScheme;
      if (harmonyScheme === 'splitComplementary') {
        harmonyDisplay = 'Split Comp.';
      } else if (harmonyScheme === 'monochromatic') {
        harmonyDisplay = 'Monochrome';
      } else if (harmonyScheme === 'complementary') {
        harmonyDisplay = 'Complement';
      } else if (harmonyScheme === 'analogous') {
        harmonyDisplay = 'Analogous';
      } else if (harmonyScheme === 'triadic') {
        harmonyDisplay = 'Triadic';
      } else if (harmonyScheme === 'tetradic') {
        harmonyDisplay = 'Tetradic';
      } else if (harmonyScheme === 'square') {
        harmonyDisplay = 'Square';
      } else if (harmonyScheme === 'normal') {
        harmonyDisplay = 'Standard';
      }
      
      harmonyTag.textContent = harmonyDisplay;
      shadeTags.appendChild(harmonyTag);
      
      clickableContainer.appendChild(shadeTags);
      
      // NEW: Add preview image container
      const previewContainer = document.createElement('div');
      previewContainer.classList.add('palette-preview-container');
      clickableContainer.appendChild(previewContainer);
      
      // Create small preview canvas
      const previewCanvas = document.createElement('canvas');
      previewCanvas.width = 200;
      previewCanvas.height = 200;
      previewCanvas.classList.add('palette-preview-canvas');
      previewContainer.appendChild(previewCanvas);
      
      // Generate the preview using the full palette
      generatePreview(previewCanvas, paletteColors, i);

      // Add click handler to use the FULL palette when clicked
      clickableContainer.addEventListener('click', function() {
        try {
          const paletteIndex = parseInt(this.dataset.paletteIndex, 10);

          console.log(`Palette clicked: base[${paletteIndex}]`);

          // Call processPallet with 'base' collection and paletteIndex
          if (typeof window.processPallet === 'function') {
            const fullPalette = window.basePaletteColors[paletteIndex];
            if (fullPalette && fullPalette.length > 0) {
              window.processPallet(null, 1, null, 0, null, fullPalette, 'base', paletteIndex);
            } else {
              console.error(`No full palette found in basePaletteColors[${paletteIndex}]`);
            }
          }
        } catch (e) {
          console.error("Error in palette click handler:", e);
        }
      });
      
      // NEW: Display the representative colors underneath the preview
      const swatchContainer = document.createElement('div');
      swatchContainer.classList.add('swatch-container');
      clickableContainer.appendChild(swatchContainer);

      // Prepare display colors - consistent count for all palettes
      const displayColors = prepareDisplayColors(paletteColors);

      // Display color swatches
      displayColors.forEach((color, idx) => {
        const swatch = document.createElement('div');
        swatch.classList.add('color-swatch');
        swatch.style.backgroundColor = `rgb(${color.join(',')})`;

        // Convert RGB to HEX for tooltip
        const hexColor = rgbToHex(color[0], color[1], color[2]);

        // Just show the HEX value in the tooltip
        swatch.title = hexColor;

        // Add special class for base swatches if needed
        swatch.classList.add('base-swatch');

        swatchContainer.appendChild(swatch);
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

        const fullPalette = window.basePaletteColors[i];
        if (!fullPalette || fullPalette.length === 0) {
          console.error('No full palette found to display');
          return;
        }

        showFullPaletteModal(fullPalette, 'base', i);
      });
    }

    // Add event listeners for shuffle buttons
    document.querySelectorAll('[id^="base_shufflePalette_"]').forEach(button => {
      const paletteIndex = parseInt(button.id.split('_').pop(), 10);

      // Remove existing click listeners
      const newButton = button.cloneNode(true);
      button.parentNode.replaceChild(newButton, button);

      newButton.addEventListener('click', async function(e) {
        e.stopPropagation(); // Prevent triggering palette selection

        try {
          // Get current shade category and harmony scheme for this palette
          let shadeCategory = 'regular';
          let harmonyScheme = 'normal';
          
          if (window.basePaletteColors && window.basePaletteColors.shadeCategories &&
              window.basePaletteColors.shadeCategories[paletteIndex]) {
            shadeCategory = window.basePaletteColors.shadeCategories[paletteIndex];
          }
          
          if (window.basePaletteColors && window.basePaletteColors.harmonySchemes &&
              window.basePaletteColors.harmonySchemes[paletteIndex]) {
            harmonyScheme = window.basePaletteColors.harmonySchemes[paletteIndex];
          }
          
          // Add harmony and shade info to the color object
          const colorWithInfo = [...color];
          colorWithInfo.harmonyScheme = harmonyScheme;
          colorWithInfo.shadeType = shadeCategory;
          
          // Generate a new shuffled palette that maintains the shade and harmony types
          const newPalette = generateBaseColorPalettes(colorWithInfo, backgroundColorIndex)[0];

          // Store the new palette
          window.basePaletteColors[paletteIndex] = [...newPalette];
          
          // Update shade category and harmony scheme
          if (!window.basePaletteColors.shadeCategories) {
            window.basePaletteColors.shadeCategories = {};
          }
          window.basePaletteColors.shadeCategories[paletteIndex] = shadeCategory;
          
          if (!window.basePaletteColors.harmonySchemes) {
            window.basePaletteColors.harmonySchemes = {};
          }
          window.basePaletteColors.harmonySchemes[paletteIndex] = harmonyScheme;

          // Update localStorage
          try {
            localStorage.setItem('basePaletteColors', JSON.stringify(window.basePaletteColors));
          } catch (e) {
            console.warn("Could not update basePaletteColors in localStorage:", e);
          }

          // Update the display
          const paletteContainer = document.getElementById(`base_colorPalette_${paletteIndex}`);
          if (!paletteContainer) return;

          paletteContainer.innerHTML = '';

          // Create clickable container
          const clickableContainer = document.createElement('div');
          clickableContainer.classList.add('palette-clickable-container');
          paletteContainer.appendChild(clickableContainer);

          // Store data
          clickableContainer.dataset.paletteIndex = paletteIndex;
          clickableContainer.dataset.collection = 'base';
          clickableContainer.dataset.shadeCategory = shadeCategory;
          clickableContainer.dataset.harmonyScheme = harmonyScheme;
          
          // Add scheme tags
          const shadeTags = document.createElement('div');
          shadeTags.className = 'scheme-tags';
          
          // Add shade tag
          const shadeTag = document.createElement('span');
          shadeTag.className = 'shade-tag';
          shadeTag.textContent = shadeCategory.charAt(0).toUpperCase() + shadeCategory.slice(1);
          shadeTags.appendChild(shadeTag);
          
          // Add harmony tag
          const harmonyTag = document.createElement('span');
          harmonyTag.className = 'harmony-tag';
          
          // Format harmony scheme for display
          let harmonyDisplay = harmonyScheme;
          if (harmonyScheme === 'splitComplementary') {
            harmonyDisplay = 'Split Comp.';
          } else if (harmonyScheme === 'monochromatic') {
            harmonyDisplay = 'Monochrome';
          } else if (harmonyScheme === 'complementary') {
            harmonyDisplay = 'Complement';
          } else if (harmonyScheme === 'analogous') {
            harmonyDisplay = 'Analogous';
          } else if (harmonyScheme === 'triadic') {
            harmonyDisplay = 'Triadic';
          } else if (harmonyScheme === 'tetradic') {
            harmonyDisplay = 'Tetradic';
          } else if (harmonyScheme === 'square') {
            harmonyDisplay = 'Square';
          } else if (harmonyScheme === 'normal') {
            harmonyDisplay = 'Standard';
          }
          
          harmonyTag.textContent = harmonyDisplay;
          shadeTags.appendChild(harmonyTag);
          
          clickableContainer.appendChild(shadeTags);
          
          // NEW: Add preview image container
          const previewContainer = document.createElement('div');
          previewContainer.classList.add('palette-preview-container');
          clickableContainer.appendChild(previewContainer);
          
          // Create small preview canvas
          const previewCanvas = document.createElement('canvas');
          previewCanvas.width = 200;
          previewCanvas.height = 200;
          previewCanvas.classList.add('palette-preview-canvas');
          previewContainer.appendChild(previewCanvas);
          
          // Generate the preview using the new palette
          await generatePreview(previewCanvas, newPalette, paletteIndex);
          
          // NEW: Add swatch container
          const swatchContainer = document.createElement('div');
          swatchContainer.classList.add('swatch-container');
          clickableContainer.appendChild(swatchContainer);

          // Add click handler
          clickableContainer.addEventListener('click', function() {
            try {
              const paletteIndex = parseInt(this.dataset.paletteIndex, 10);
              
              console.log(`Palette clicked: base[${paletteIndex}]`);
              
              // Get the FULL palette from storage
              const fullPalette = window.basePaletteColors[paletteIndex];
              
              if (!fullPalette || fullPalette.length === 0) {
                console.error(`No palette found for base[${paletteIndex}]`);
                return;
              }
              
              // Call processPallet with the FULL palette
              if (typeof window.processPallet === 'function') {
                window.processPallet(null, 1, null, 0, null, fullPalette, 'base', paletteIndex);
              }
            } catch (e) {
              console.error("Error in palette click handler:", e);
            }
          });
          
          // Prepare display colors
          const displayColors = prepareDisplayColors(newPalette);
          
          // Add color swatches
          displayColors.forEach((color, idx) => {
            const swatch = document.createElement('div');
            swatch.classList.add('color-swatch');
            swatch.style.backgroundColor = `rgb(${color.join(',')})`;

            // Convert RGB to HEX for tooltip
            const hexColor = rgbToHex(color[0], color[1], color[2]);

            // Just show the HEX value in tooltip
            swatch.title = hexColor;

            swatch.classList.add('base-swatch');
            swatchContainer.appendChild(swatch);
          });

          // Add "Show All" button
          const showAllButton = document.createElement('div');
          showAllButton.classList.add('show-all-colors-btn');
          showAllButton.innerHTML = '+';
          showAllButton.title = 'Show all colors in palette';
          clickableContainer.appendChild(showAllButton);

          showAllButton.addEventListener('click', function(e) {
            e.stopPropagation();
            showFullPaletteModal(window.basePaletteColors[paletteIndex], 'base', paletteIndex);
          });

        } catch (e) {
          console.error("Error in shuffle button handler:", e);
        }
      });
    });

    // Add event listeners for apply buttons
    document.querySelectorAll('[id^="base_applyButton_"]').forEach(button => {
      const paletteIndex = parseInt(button.id.split('_').pop(), 10);

      // Remove existing click listeners
      const newButton = button.cloneNode(true);
      button.parentNode.replaceChild(newButton, button);

      newButton.addEventListener('click', function(e) {
        e.stopPropagation(); // Prevent triggering palette selection

        try {
          // Get the full palette array
          const fullPalette = window.basePaletteColors[paletteIndex];
          
          if (!fullPalette || fullPalette.length === 0) {
            console.error(`No palette found for base[${paletteIndex}]`);
            return;
          }
          
          console.log(`Applying palette ${paletteIndex} with ${fullPalette.length} colors`);
          
          // Pass the actual palette array to processPallet
          if (typeof window.processPallet === 'function') {
            window.processPallet(null, 1, null, 0, null, fullPalette, 'base', paletteIndex);
          }
        } catch (e) {
          console.error("Error in apply button handler:", e);
        }
      });
    });
    
    // Set up lazy loading for palette previews
    setupLazyLoadingForPalettes();
    
    // Add the necessary CSS if it doesn't exist
    if (!document.getElementById('palette-preview-styles')) {
      const styleElement = document.createElement('style');
      styleElement.id = 'palette-preview-styles';
      styleElement.textContent = `
        .palette-clickable-container {
            display: flex;
            flex-direction: column;
            cursor: pointer;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            position: relative;
            width: 200px;
            margin-bottom: 15px;
        }
        
        .palette-clickable-container:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .palette-preview-container {
            width: 200px;
            height: 200px;
            overflow: hidden;
            position: relative;
            background-color: white;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .palette-preview-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.7);
            z-index: 1;
        }
        
        .palette-preview-container::after {
            content: 'Loading...';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #666;
            z-index: 2;
        }
        
        .preview-ready .palette-preview-container::before,
        .preview-ready .palette-preview-container::after {
            display: none;
        }
        
        .palette-preview-canvas {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        
        .swatch-container {
            display: flex;
            justify-content: space-around;
            padding: 5px;
            background-color: #f5f5f5;
            border-top: 1px solid #ddd;
        }
        
        .color-swatch {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 1px solid #ddd;
            margin: 0 2px;
        }
        
        .ss-swatch {
            border-color: #d0d0ff;
        }
        
        .aw-swatch {
            border-color: #ffd0d0;
        }
        
        .base-swatch {
            border-color: #d0ffd0;
        }
        
        .show-all-colors-btn {
            position: absolute;
            top: 5px;
            right: 5px;
            width: 25px;
            height: 25px;
            background-color: rgba(255,255,255,0.8);
            color: #333;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-weight: bold;
            z-index: 3;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        
        .show-all-colors-btn:hover {
            background-color: rgba(255,255,255,0.95);
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        
        .full-palette-modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.7);
        }
        
        .full-palette-modal-content {
            background-color: #fff;
            margin: 10% auto;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            width: 80%;
            max-width: 600px;
            position: relative;
        }
        
        .close-palette-modal {
            position: absolute;
            top: 10px;
            right: 15px;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .palette-modal-title {
            text-align: center;
            margin-bottom: 20px;
            color: #333;
        }
        
        .all-colors-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
        }
        
        .full-palette-color {
            width: 80px;
            height: 80px;
            border-radius: 8px;
            position: relative;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .color-info {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: rgba(0,0,0,0.6);
            color: white;
            font-size: 10px;
            padding: 3px;
            text-align: center;
            opacity: 0;
            transition: opacity 0.2s;
        }
        
        .full-palette-color:hover .color-info {
            opacity: 1;
        }
        
        .palette-number {
            position: absolute;
            top: 5px;
            left: 5px;
            background-color: rgba(0,0,0,0.6);
            color: white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            z-index: 3;
        }
        
        .scheme-tags {
            position: absolute;
            top: 5px;
            right: 34px;
            display: flex;
            gap: 4px;
            z-index: 3;
        }
        
        .shade-tag, .harmony-tag {
            background-color: rgba(0,0,0,0.6);
            color: white;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 10px;
            white-space: nowrap;
        }
        
        .harmony-tag {
            background-color: rgba(60,60,120,0.8);
        }
        
        .base-color-filters {
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
            align-items: center;
        }
        
        .filter-dropdown {
            min-width: 140px;
        }
        
        .filter-dropdown select {
            width: 100%;
            padding: 6px 10px;
            border-radius: 4px;
            border: 1px solid #ced4da;
            background-color: white;
        }
      `;
      document.head.appendChild(styleElement);
    }
  } catch (error) {
    console.error("Error in selectBaseColor:", error);
  }
}

// Create base color dropdown filters
function createBaseColorDropdownFilters(baseColor) {
  // Remove any existing filter container
  const existingFilters = document.querySelector('.base-color-filters');
  if (existingFilters) {
    existingFilters.remove();
  }
  
  // Create filter container
  const filterContainer = document.createElement('div');
  filterContainer.className = 'base-color-filters';
  
  // Create filter label for harmony
  const harmonyLabel = document.createElement('div');
  harmonyLabel.className = 'filter-label';
  harmonyLabel.textContent = 'Harmony:';
  
  // Create harmony dropdown
  const harmonyDropdown = document.createElement('div');
  harmonyDropdown.className = 'filter-dropdown harmony-dropdown';
  
  const harmonySelect = document.createElement('select');
  harmonySelect.id = 'harmony-filter';
  harmonySelect.className = 'form-select';
  
  // Add harmony options
  const harmonyOptions = [
    { value: 'all', label: 'All Harmonies' },
    { value: 'normal', label: 'Standard' },
    { value: 'monochromatic', label: 'Monochromatic' },
    { value: 'analogous', label: 'Analogous' },
    { value: 'complementary', label: 'Complementary' },
    { value: 'splitComplementary', label: 'Split Complementary' },
    { value: 'triadic', label: 'Triadic' },
    { value: 'tetradic', label: 'Tetradic' },
    { value: 'square', label: 'Square' }
  ];
  
  harmonyOptions.forEach(option => {
    const optionElement = document.createElement('option');
    optionElement.value = option.value;
    optionElement.textContent = option.label;
    harmonySelect.appendChild(optionElement);
  });
  
  harmonyDropdown.appendChild(harmonySelect);
  
  // Create filter label for shade
  const shadeLabel = document.createElement('div');
  shadeLabel.className = 'filter-label';
  shadeLabel.textContent = 'Shade:';
  
  // Create shade dropdown
  const shadeDropdown = document.createElement('div');
  shadeDropdown.className = 'filter-dropdown shade-dropdown';
  
  const shadeSelect = document.createElement('select');
  shadeSelect.id = 'shade-filter';
  shadeSelect.className = 'form-select';
  
  // Add shade options
  const shadeOptions = [
    { value: 'all', label: 'All Shades' },
    { value: 'faint', label: 'Faint' },
    { value: 'regular', label: 'Regular' },
    { value: 'dark', label: 'Dark' }
  ];
  
  shadeOptions.forEach(option => {
    const optionElement = document.createElement('option');
    optionElement.value = option.value;
    optionElement.textContent = option.label;
    shadeSelect.appendChild(optionElement);
  });
  
  shadeDropdown.appendChild(shadeSelect);
  
  // Add event listeners to dropdowns
  harmonySelect.addEventListener('change', function() {
    applyFilters(this.value, shadeSelect.value, baseColor);
  });
  
  shadeSelect.addEventListener('change', function() {
    applyFilters(harmonySelect.value, this.value, baseColor);
  });
  
  // Add all elements to filter container
  filterContainer.appendChild(harmonyLabel);
  filterContainer.appendChild(harmonyDropdown);
  filterContainer.appendChild(shadeLabel);
  filterContainer.appendChild(shadeDropdown);
  
  // Add filter container before the palettes container
  const palettesSection = document.querySelector('.base-palettes-section');
  if (palettesSection) {
    const palettesContainer = palettesSection.querySelector('.base-palettes-container');
    palettesSection.insertBefore(filterContainer, palettesContainer);
  }
}

// Apply filters to the displayed palettes
function applyFilters(harmonyFilter, shadeFilter, baseColor) {
  console.log(`Applying filters - Harmony: ${harmonyFilter}, Shade: ${shadeFilter}`);
  
  // Get all palette rows
  const paletteRows = document.querySelectorAll('.palette-row');
  let visibleCount = 0;
  
  paletteRows.forEach(row => {
    // Get the palette's shade category and harmony scheme
    const shadeCategory = row.dataset.shadeCategory || 'regular';
    const harmonyScheme = row.dataset.harmonyScheme || 'normal';
    
    // Show or hide based on filters
    const matchesShade = shadeFilter === 'all' || shadeFilter === shadeCategory;
    const matchesHarmony = harmonyFilter === 'all' || harmonyFilter === harmonyScheme;
    
    if (matchesShade && matchesHarmony) {
      row.style.display = 'flex';
      visibleCount++;
    } else {
      row.style.display = 'none';
    }
  });
  
  console.log(`Filters applied - ${visibleCount} palettes visible`);
}