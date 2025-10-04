
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def to_grayscale(img):
    if img.ndim != 3 or img.shape[2] != 3:
        raise ValueError("Input image must be a 3-channel RGB image.")

    gsw = np.array([0.2126,0.7152,0.0722]) # RGB to grayscale weights

    return pd.DataFrame(np.dot(img[..., :3], gsw))

def load_terrain_data(file_path, invert=False):
    try:
        data = to_grayscale(plt.imread(file_path))
        print(f"Terrain elevation data loaded from {file_path}")
        if invert:
            data = data.map(lambda x: x-1).abs()
        return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
