# apps\tif_to_picker\urls.py
from django.urls import path
from .views import upload_tiff,single_layer_color_picker,export_tiff,process_svg_upload,analyze_color
from . import views
from apps.subscription_module.views import create_favorite_palette,remove_favorite_palette,get_favorites
urlpatterns = [
    path('', upload_tiff, name='upload_tiff'),
    path('projects/<int:user_id>/<int:project_id>/edit/', upload_tiff, name='edit-project'),
    path('color-picker/', single_layer_color_picker, name='single_layer_color_picker'),
    path('export_tiff/', export_tiff, name='export_tiff'),
    path('upload-svg/', process_svg_upload, name='process_svg_upload'),
    path('analyze-color/', analyze_color, name='analyze-color'),
    path('inspiration-pdfs/', views.inspiration_view, name='inspiration_pdfs'),
    path('api/palettes/', views.get_palettes, name='get_palettes'),
    
    # Add the new URL pattern for layer-specific palettes
    path('api/palettes-for-layers/<int:total_layers>/', views.get_palettes_for_layers, name='get_palettes_for_layers'),
    path('api/palettes/favorite/', create_favorite_palette, name='create-favorite-palette'),
    path('api/palettes/favorite/<int:palette_id>/',remove_favorite_palette, name='remove-favorite-palette'),
    path('api/palettes/favorites/', get_favorites, name='get-favorites'),
    

]
 