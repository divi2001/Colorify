# In a file named serializers.py in the same directory as your views.py

from rest_framework import serializers
from .models import Palette

class PaletteSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source='creator.username', read_only=True)

    class Meta:
        model = Palette
        fields = ['id', 'name', 'creator_username', 'created_at', 'updated_at', 
                  'favorites_count', 'num_colors', 'base_color', 'base_color_rgb', 'type']