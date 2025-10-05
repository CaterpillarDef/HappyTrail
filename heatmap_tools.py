
import numpy as np
import pandas as pd

def normalize_heatmap(heatmap):
    min_val = heatmap.min(axis=None)
    max_val = heatmap.max(axis=None)

    if max_val - min_val == 0:
        return heatmap - min_val  # Avoid division by zero if all values are the same

    normalized_heatmap = (heatmap - min_val) / (max_val - min_val)
    return normalized_heatmap

def colorize_path(img, green=False,blue=True):
    if green:
        blue = False
    else:
        blue = True
    if isinstance(img, pd.DataFrame):
        bw_array = img.values
    else:
        bw_array = img

    # Create RGB image with white background (1,1,1)
    height, width = bw_array.shape
    rgb_image = np.ones((height, width, 3), dtype=np.float32)

    # Path values are 0 in the overlay, so we use (1-bw_array) to identify path pixels
    path_mask = (1 - bw_array)

    # Set path color (keep white background where path_mask is 0)
    if green:
        # For green path: (0,1,0)
        rgb_image[:,:,0] -= path_mask  # Reduce red channel to 0 for path
        rgb_image[:,:,2] -= path_mask  # Reduce blue channel to 0 for path
    else:  # blue
        # For blue path: (0,0,1)
        rgb_image[:,:,0] -= path_mask  # Reduce red channel to 0 for path
        rgb_image[:,:,1] -= path_mask  # Reduce green channel to 0 for path

    return rgb_image
