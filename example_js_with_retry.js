// Example: How to handle the busy response with automatic retry

async function applyMultipleColorMappings(imageData, colorMappings, useJimp = false, retryCount = 0) {
    // Backend processing with Jimp
    if (useJimp) {
        console.log("Using Jimp for backend processing");
        try {
            const formData = new FormData();
            if (typeof imageData === 'string' && imageData.startsWith('data:image')) {
                try {
                    const fetchResponse = await fetch(imageData);
                    if (!fetchResponse.ok) throw new Error("Failed to fetch image data");
                    const blob = await fetchResponse.blob();
                    formData.append('image', blob, 'image.png');
                } catch (blobError) {
                    formData.append('imageData', imageData);
                }
            } else {
                formData.append('imageData', imageData);
            }
            formData.append('colorMappings', JSON.stringify(colorMappings));
            
            // Updated URL to use Django endpoint
            const response = await fetch('/tif-editor/api/process-image-with-jimp/', {
                method: 'POST',
                body: formData,
            });
            
            if (response.status === 503) {
                // Server is busy processing another request
                const result = await response.json();
                
                if (result.busy && retryCount < 5) {
                    // Wait and retry (exponential backoff)
                    const waitTime = Math.min(1000 * Math.pow(2, retryCount), 5000);
                    console.log(`Server busy, retrying in ${waitTime}ms... (attempt ${retryCount + 1}/5)`);
                    
                    await new Promise(resolve => setTimeout(resolve, waitTime));
                    return applyMultipleColorMappings(imageData, colorMappings, useJimp, retryCount + 1);
                } else {
                    throw new Error("Server is busy. Please try again later.");
                }
            }
            
            if (!response.ok) {
                throw new Error(`Backend processing failed: ${response.status}`);
            }
            
            const result = await response.json();
            if (!result.success || !result.processedImage) {
                throw new Error("Backend returned invalid response");
            }
            
            return result.processedImage;
        } catch (error) {
            console.error('Error with Jimp processing:', error);
            // Fallback to client-side processing
            return this.applyMultipleColorMappings(imageData, colorMappings, false);
        }
    }
    
    // ... rest of your client-side processing code
}
