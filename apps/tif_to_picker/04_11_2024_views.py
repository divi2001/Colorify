import os
import psdtags
import numpy as np
from PIL import Image
from collections import Counter
from psdtags import PsdChannelId
from .forms import TiffUploadForm
from django.shortcuts import render
from psdtags.psdtags import TiffImageSourceData, PsdChannelId
from tifffile import TiffFile, imshow,imwrite
from matplotlib import pyplot


def upload_tiff(request):
    if request.method == 'POST':
        form = TiffUploadForm(request.POST, request.FILES)
        if form.is_valid():
            tiff_file = request.FILES['tiff_file']
            file_path = os.path.join('media', tiff_file.name)
            print(file_path)
            # Check if file already exists
            if not os.path.exists(file_path):
                with open(file_path, 'wb+') as destination:
                    for chunk in tiff_file.chunks():
                        destination.write(chunk)
            # with open(file_path, 'wb+') as destination:
            #     for chunk in tiff_file.chunks():
            #         destination.write(chunk)

            # Process the TIFF file

            layers = extract_layers(file_path, 'media/output/'+tiff_file.name)

            return render(request, 'single_layers.html', {'layers': layers})
            # return render(request, 'layers.html', {'layers': layers})
    else:
        form = TiffUploadForm()
    return render(request, 'upload.html', {'form': form})


def get_layer_image(layer):
    try:
        channels_data = []
        for channel in layer.channels:
            if channel.channelid in [PsdChannelId.CHANNEL0, PsdChannelId.CHANNEL1, PsdChannelId.CHANNEL2]:
                if channel.data.ndim == 2:
                    channels_data.append(channel.data)
                else:
                    print(
                        f"Unexpected channel data shape: {channel.data.shape}")

        if len(channels_data) == 3:
            image_data = np.stack(channels_data, axis=-1)
            return image_data
        else:
            print(f"Unexpected number of channels: {len(channels_data)}")
            return None
    except Exception as e:
        print(f"Error retrieving layer image: {str(e)}")
        return None

def extract_layers(file_path, output_dir):
    isd = TiffImageSourceData.fromtiff(file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    layers_info = []
    if isd.layers:

        for layer in isd.layers:

            image = layer.asarray()
            image_pros = get_layer_image(layer)
            unique_colors = []
            layer_position_from_top = layer.offset[0]
            layer_position_from_left = layer.offset[1]
            if image.size > 0:
                layer_output_path = os.path.join(output_dir, f"{layer.name}.png")  # Save as PNG
                if not os.path.exists(layer_output_path):
                    pyplot.imsave(layer_output_path, image, cmap='gray' if image.ndim == 2 else None)
                channels = {}
                layer_width, layer_height = None, None
                unique_colors = []

                for channel in layer.channels:
                    channel_data = np.array(channel.data)
                    if layer_width is None and layer_height is None:
                        layer_height, layer_width = channel_data.shape

                    if channel_data.shape != (layer_height, layer_width):
                        print(
                            f"Skipping layer {layer.name}, channel size mismatch.")
                        continue
                    if channel.channelid == psdtags.PsdChannelId.CHANNEL0:  # Red
                        channels['R'] = channel_data
                    elif channel.channelid == psdtags.PsdChannelId.CHANNEL1:  # Green
                        channels['G'] = channel_data
                    elif channel.channelid == psdtags.PsdChannelId.CHANNEL2:  # Blue
                        channels['B'] = channel_data
                if 'R' in channels and 'G' in channels and 'B' in channels:
                    try:
                        rgb_array = image_pros
                        # Collect unique colors from the layer
                        # Reshape to a list of RGB tuples
                        all_colors = rgb_array.reshape(-1, 3)
                        unique_colors = [tuple(color)
                                        for color in np.unique(all_colors, axis=0)]

                        # Get the three most common colors
                        color_counts = Counter(tuple(color)
                                            for color in all_colors)
                        most_common_colors = color_counts.most_common(10)
                        most_common_colors_rgb = [
                            list(color[0]) for color in most_common_colors]

                        # Convert the most common colors to hex
                        most_common_colors_hex = ['#{:02x}{:02x}{:02x}'.format(
                            color[0], color[1], color[2]) for color in most_common_colors_rgb]
                        avg_color = np.mean(rgb_array, axis=(0, 1)).astype(
                            int)  # Get the average for R, G, B
                        avg_color_hex = '#{:02x}{:02x}{:02x}'.format(avg_color[0], avg_color[1],
                                                                    avg_color[2])  # Convert to hex
                        max_color_value = np.max(avg_color)  # or max(avg_color)
                        min_color_value = np.min(avg_color)  # or min(avg_color)
                        layers_info.append({
                            'name': layer.name,
                            'path': layer_output_path,
                            'unique_colors': unique_colors,
                            'max_color_value': max_color_value,
                            'min_color_value': min_color_value,
                            'most_common_colors': most_common_colors_hex,
                            'color': avg_color_hex,  # Add most common colors
                            'layer_position_from_top': layer_position_from_top,  # Add most common colors
                            'layer_position_from_left': layer_position_from_left,  # Add most common colors
                        })
                    except Exception as e:
                        print(f"Error processing layer {layer.name}: {str(e)}")
            else:
                print(f'Layer {layer.name!r} image size is zero')
    return layers_info



def single_layer_color_picker(request):
    tiff_file = request.FILES['tiff_file']
    # print(tiff_file)
    file_path = os.path.join('media', tiff_file.name)
    # print(file_path)
    with open(file_path, 'wb+') as destination:
        for chunk in tiff_file.chunks():
            destination.write(chunk)

    # Process the TIFF file

    layers = extract_layers(file_path, 'media/output/'+tiff_file.name)

    return render(request, 'single_layers.html', {'layers': layers})
    # return render(request, "layer_color_picker.html")