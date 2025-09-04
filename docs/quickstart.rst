Quick Start Guide
==================

Welcome to Colorify Studio! This guide will help you get started quickly with the basic features of our AI-powered color matching platform.

Prerequisites
-------------

Before starting, ensure you have:

* Completed the :doc:`installation` process
* A running Colorify Studio instance
* Sample TIFF or PSD files to work with
* A user account (sign up if you haven't already)

First Steps
-----------

**1. Access the Application**

Open your web browser and navigate to:

.. code-block:: text

   http://localhost:8000  # For local development
   # OR
   https://your-domain.com  # For production

**2. Create an Account**

If you don't have an account:

1. Click "Sign Up" on the homepage
2. Fill in your details:
   - Username
   - Email address
   - Password
   - Confirm password
3. Check your email for verification
4. Click the verification link to activate your account

**3. Login**

1. Click "Login" on the homepage
2. Enter your credentials
3. You'll be redirected to the main application

Your First Project
------------------

**Step 1: Upload a File**

1. Navigate to the TIF Editor: ``/tif-editor/``
2. Click "Choose File" or drag and drop a TIFF/PSD file
3. Supported formats:
   - TIFF files with multiple layers
   - PSD files (Photoshop documents)
   - Maximum file size: 50MB

**Step 2: Analyze Layers**

Once uploaded, Colorify will automatically:

1. Extract all layers from your file
2. Display them in the interface
3. Show a preview of each layer
4. Provide layer management tools

**Step 3: Color Analysis**

1. Click on any layer to select it
2. The color analysis panel will show:
   - Dominant colors in the layer
   - Color distribution
   - Hex/RGB values
3. Use the color picker to select specific colors

**Step 4: Generate Palettes**

1. Click "Generate Palette" 
2. Choose from different palette types:
   - Monochromatic
   - Complementary
   - Triadic
   - Analogous
   - Custom
3. Adjust the number of colors (3-10)
4. Save your favorite palettes

Basic Workflows
---------------

**Workflow 1: Simple Color Replacement**

.. code-block:: text

   1. Upload your design file
   2. Select the layer to modify
   3. Choose the color to replace
   4. Pick a new color from the palette
   5. Apply the change
   6. Export the modified file

**Workflow 2: Palette-Based Design**

.. code-block:: text

   1. Start with inspiration images
   2. Generate color palettes
   3. Save preferred palettes
   4. Apply palettes to new designs
   5. Fine-tune individual colors
   6. Export final designs

**Workflow 3: Batch Processing**

.. code-block:: text

   1. Upload multiple design files
   2. Create a master palette
   3. Apply consistent colors across files
   4. Review and adjust as needed
   5. Export all modified files

Understanding the Interface
---------------------------

**Main Navigation**

* **Home**: Landing page and overview
* **TIF Editor**: Main workspace for file editing
* **Inspiration**: Browse color inspiration gallery
* **Plans**: Subscription management
* **Profile**: User account settings

**TIF Editor Components**

* **File Upload Area**: Drag and drop or browse for files
* **Layer Panel**: Shows all extracted layers
* **Color Analysis Panel**: Displays color information
* **Palette Generator**: Creates harmonious color schemes
* **Export Options**: Download modified files

**Color Tools**

* **Color Picker**: Select specific colors from images
* **Palette Generator**: Create harmonious color schemes
* **Color History**: Track recently used colors
* **Favorites**: Save preferred color combinations

Working with Subscriptions
---------------------------

**Free Tier Limitations**

* 5 file uploads per month
* Basic color analysis
* Standard export formats
* Limited storage (100MB)

**Premium Features**

* Unlimited file uploads
* Advanced AI color matching
* Batch processing
* Priority support
* Additional export formats
* Extended storage

**Upgrading Your Plan**

1. Go to ``/plans/`` or click "Upgrade" 
2. Choose your preferred plan
3. Complete payment via Razorpay
4. Enjoy premium features immediately

Common Tasks
------------

**Task 1: Extract Colors from an Image**

.. code-block:: python

   # Example of what happens behind the scenes
   1. Upload image → Colorify processes layers
   2. AI analyzes → Identifies dominant colors
   3. Results display → Interactive color palette
   4. User selects → Colors for further use

**Task 2: Create a Brand Color Palette**

1. Upload your brand logo or assets
2. Use "Extract Palette" feature
3. Fine-tune the extracted colors
4. Save as "Brand Palette"
5. Apply to future projects

**Task 3: Match Colors Across Designs**

1. Set a reference color from one design
2. Upload target designs
3. Use "Color Match" feature
4. Review suggested matches
5. Apply and export

Tips for Best Results
---------------------

**File Preparation**

* Use high-resolution images (300 DPI minimum)
* Ensure layers are properly named in your source files
* Avoid flattened images for better layer separation
* Save original files as backup

**Color Analysis**

* Work in good lighting conditions when reviewing colors
* Consider color calibration for your monitor
* Test color outputs on your target medium
* Save successful color combinations

**Performance Optimization**

* Keep file sizes under 25MB for faster processing
* Close unused browser tabs
* Use a stable internet connection
* Clear browser cache if experiencing issues

Next Steps
----------

Now that you're familiar with the basics:

1. **Explore Advanced Features**: Check out the :doc:`user_guide/index`
2. **Learn the API**: See :doc:`developer_guide/api_reference`
3. **Customize Settings**: Visit :doc:`configuration`
4. **Join the Community**: Connect with other users

**Helpful Resources**

* :doc:`user_guide/uploading_files` - Detailed file upload guide
* :doc:`user_guide/color_analysis` - Advanced color analysis
* :doc:`user_guide/palette_generation` - Master palette creation
* :doc:`user_guide/subscription_management` - Manage your account

Getting Help
------------

If you need assistance:

* **In-App Help**: Click the "?" icon in any interface
* **Documentation**: Browse these docs for detailed guides
* **Support Email**: support@colorifystudio.ai
* **Community Forum**: Join discussions with other users

**Reporting Issues**

Found a bug? Help us improve:

1. Note the steps that led to the issue
2. Include your browser and OS information
3. Take a screenshot if relevant
4. Email details to support@colorifystudio.ai

Congratulations! You're now ready to create amazing color-matched designs with Colorify Studio. Happy designing! 🎨 