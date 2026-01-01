"""
Flask API Server for Palette-Based Image Recoloring
Compatible with existing frontend that sends colorMappings
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
import json
from PIL import Image
import sys
import os

# Import the standalone recoloring module
from palette_recolor_standalone import PaletteRecolor

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize recolorer
recolorer = PaletteRecolor(sample_level=16, luminance_flag=True)


def decode_image_data(image_data):
    """
    Decode image data from various formats.
    Supports: base64 data URL, raw base64, or file upload
    """
    try:
        # If it's a data URL (data:image/png;base64,...)
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            # Extract base64 part
            base64_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(base64_data)
        elif isinstance(image_data, str):
            # Try as raw base64
            image_bytes = base64.b64decode(image_data)
        else:
            # Assume it's already bytes
            image_bytes = image_data
        
        # Open as PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    except Exception as e:
        raise ValueError(f"Failed to decode image: {str(e)}")


def encode_image_to_base64(image):
    """
    Encode PIL Image to base64 data URL.
    """
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f'data:image/png;base64,{image_base64}'


@app.route('/api/process-image-with-jimp', methods=['POST'])
def process_image_with_jimp():
    """
    Main endpoint compatible with your existing frontend.
    Accepts colorMappings and applies palette-based recoloring.
    
    Expected request:
    - Form data with 'image' file OR 'imageData' base64
    - 'colorMappings' JSON string with format:
      [
        {"originalColor": [r, g, b], "targetColor": [r, g, b]},
        ...
      ]
    """
    try:
        print("=" * 60)
        print("Received image processing request")
        
        # Get image data
        image = None
        
        # Try to get from file upload first
        if 'image' in request.files:
            print("Loading image from file upload")
            file = request.files['image']
            image = Image.open(file.stream)
            if image.mode != 'RGB':
                image = image.convert('RGB')
        
        # Try to get from form data
        elif 'imageData' in request.form:
            print("Loading image from imageData")
            image_data = request.form['imageData']
            image = decode_image_data(image_data)
        
        # Try to get from JSON body
        elif request.is_json:
            print("Loading image from JSON body")
            data = request.json
            if 'imageData' in data:
                image = decode_image_data(data['imageData'])
            elif 'image' in data:
                image = decode_image_data(data['image'])
        
        if image is None:
            return jsonify({
                'success': False,
                'error': 'No image data provided. Send as "image" file or "imageData" base64'
            }), 400
        
        print(f"Image loaded: {image.size}")
        
        # Get color mappings
        color_mappings_str = None
        if 'colorMappings' in request.form:
            color_mappings_str = request.form['colorMappings']
        elif request.is_json and 'colorMappings' in request.json:
            color_mappings_str = json.dumps(request.json['colorMappings'])
        
        if not color_mappings_str:
            return jsonify({
                'success': False,
                'error': 'No colorMappings provided'
            }), 400
        
        # Parse color mappings
        color_mappings = json.loads(color_mappings_str)
        print(f"Color mappings: {len(color_mappings)} pairs")
        
        # Extract original and target colors
        original_colors = []
        target_colors = []
        
        for mapping in color_mappings:
            original = mapping.get('originalColor')
            target = mapping.get('targetColor')
            
            if original and target:
                # Ensure they're tuples of 3 integers
                original_colors.append(tuple([int(c) for c in original[:3]]))
                target_colors.append(tuple([int(c) for c in target[:3]]))
        
        if not original_colors or not target_colors:
            return jsonify({
                'success': False,
                'error': 'Invalid color mappings format'
            }), 400
        
        print(f"Original colors: {original_colors}")
        print(f"Target colors: {target_colors}")
        
        # Save image temporarily
        temp_input = 'temp_input.png'
        image.save(temp_input)
        
        # Apply palette-based recoloring
        print("Applying palette-based recoloring...")
        result_image = recolorer.recolor_image(
            image_path=temp_input,
            original_colors=original_colors,
            new_colors=target_colors,
            output_path=None  # Return PIL Image
        )
        
        # Clean up temp file
        if os.path.exists(temp_input):
            os.remove(temp_input)
        
        # Encode result to base64
        print("Encoding result...")
        result_base64 = encode_image_to_base64(result_image)
        
        print("Processing complete!")
        print("=" * 60)
        
        return jsonify({
            'success': True,
            'processedImage': result_base64,
            'message': 'Image processed successfully'
        })
    
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/extract-palette', methods=['POST'])
def extract_palette():
    """
    Extract color palette from an image.
    
    Expected request:
    - 'image' file OR 'imageData' base64
    - 'numColors' (optional, default: 8)
    """
    try:
        print("Extracting palette...")
        
        # Get image
        image = None
        if 'image' in request.files:
            file = request.files['image']
            image = Image.open(file.stream)
        elif 'imageData' in request.form:
            image = decode_image_data(request.form['imageData'])
        elif request.is_json:
            data = request.json
            if 'imageData' in data:
                image = decode_image_data(data['imageData'])
            elif 'image' in data:
                image = decode_image_data(data['image'])
        
        if image is None:
            return jsonify({
                'success': False,
                'error': 'No image data provided'
            }), 400
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get number of colors
        num_colors = 8
        if 'numColors' in request.form:
            num_colors = int(request.form['numColors'])
        elif request.is_json and 'numColors' in request.json:
            num_colors = int(request.json['numColors'])
        
        # Save temp file
        temp_input = 'temp_extract.png'
        image.save(temp_input)
        
        # Extract palette
        palette = recolorer.extract_palette(temp_input, num_colors=num_colors)
        
        # Clean up
        if os.path.exists(temp_input):
            os.remove(temp_input)
        
        return jsonify({
            'success': True,
            'palette': palette,
            'numColors': len(palette)
        })
    
    except Exception as e:
        print(f"Error extracting palette: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': 'Palette-Based Image Recoloring API',
        'version': '1.0'
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API documentation."""
    return '''
    <html>
    <head>
        <title>Palette-Based Recoloring API</title>
        <style>
            body { font-family: Arial; padding: 40px; max-width: 900px; margin: 0 auto; }
            h1 { color: #4CAF50; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px; }
            code { background: #e0e0e0; padding: 2px 6px; border-radius: 3px; }
            pre { background: #263238; color: #aed581; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>🎨 Palette-Based Image Recoloring API</h1>
        <p>Advanced color transfer using research-based algorithms</p>
        
        <div class="endpoint">
            <h2>POST /api/process-image-with-jimp</h2>
            <p>Apply palette-based recoloring to an image</p>
            <h3>Request (Form Data):</h3>
            <pre>
{
  "image": [file] OR "imageData": [base64],
  "colorMappings": [
    {
      "originalColor": [255, 0, 0],
      "targetColor": [0, 255, 255]
    },
    ...
  ]
}</pre>
            <h3>Response:</h3>
            <pre>
{
  "success": true,
  "processedImage": "data:image/png;base64,..."
}</pre>
        </div>
        
        <div class="endpoint">
            <h2>POST /api/extract-palette</h2>
            <p>Extract dominant colors from an image</p>
            <h3>Request:</h3>
            <pre>
{
  "image": [file] OR "imageData": [base64],
  "numColors": 8
}</pre>
            <h3>Response:</h3>
            <pre>
{
  "success": true,
  "palette": [[255, 0, 0], [0, 255, 0], ...],
  "numColors": 8
}</pre>
        </div>
        
        <div class="endpoint">
            <h2>GET /api/health</h2>
            <p>Health check endpoint</p>
        </div>
        
        <h2>Features</h2>
        <ul>
            <li>✅ Preserves luminance and gradients</li>
            <li>✅ Weighted color transfer using multiple palette colors</li>
            <li>✅ Boundary detection for valid RGB gamut</li>
            <li>✅ Trilinear interpolation for smooth transitions</li>
            <li>✅ Compatible with existing frontend code</li>
        </ul>
        
        <h2>Usage Example (JavaScript)</h2>
        <pre>
const colorMappings = [
  { originalColor: [255, 0, 0], targetColor: [0, 255, 255] },
  { originalColor: [0, 255, 0], targetColor: [255, 0, 255] }
];

const formData = new FormData();
formData.append('image', imageFile);
formData.append('colorMappings', JSON.stringify(colorMappings));

const response = await fetch('/api/process-image-with-jimp', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result.processedImage); // base64 image
        </pre>
    </body>
    </html>
    '''


if __name__ == '__main__':
    print("=" * 70)
    print("Palette-Based Image Recoloring API Server")
    print("=" * 70)
    print("Server starting on: http://0.0.0.0:8001")
    print("")
    print("Endpoints:")
    print("  POST /api/process-image-with-jimp  - Apply recoloring")
    print("  POST /api/extract-palette          - Extract color palette")
    print("  GET  /api/health                   - Health check")
    print("  GET  /                             - API documentation")
    print("")
    print("Compatible with your existing frontend code!")
    print("=" * 70)
    print("")
    
    app.run(host='localhost', port=8001, debug=True)
