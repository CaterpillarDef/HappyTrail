import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image

from terrain_node import Node

def create_terrain(size):
    raw = np.random.rand(size, size).astype(np.float64)
    sigma = max(1.0, size * 0.02)
    terrain = gaussian_filter(raw, sigma=sigma)

    nodes = [[Node(float(terrain[x, y]), x, y) for y in range(size)] for x in range(size)]

    neighbor_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1),
                        (-1, -1), (-1, 1), (1, -1), (1, 1)]

    for x in range(size):
        for y in range(size):
            current = terrain[x, y]
            e = nodes[x][y].edges
            for dx, dy in neighbor_offsets:
                nx, ny = x + dx, y + dy
                if 0 <= nx < size and 0 <= ny < size:
                    shift = round(abs(float(terrain[nx, ny] - current)),3)
                    e[(dx, dy)] = shift
    return nodes

def terrain_to_array(nodes):
    size = len(nodes)
    arr = np.empty((size, size), dtype=np.float64)
    for x in range(size):
        for y in range(size):
            arr[x, y] = float(nodes[x][y].cost)
    return arr

def save_terrain_grayscale(nodes, path, invert=True):
    arr = terrain_to_array(nodes)
    finite = np.isfinite(arr)
    if not finite.any():
        raise ValueError("No finite elevation values to render.")
    mn = arr[finite].min()
    mx = arr[finite].max()
    if mx > mn:
        norm = (arr - mn) / (mx - mn)
    else:
        norm = np.zeros_like(arr)
    norm = np.clip(norm, 0.0, 1.0)
    if invert:
        norm = 1.0 - norm
    img_u8 = (norm * 255).astype(np.uint8)
    img_u8[~finite] = 0
    img = Image.fromarray(img_u8)
    img.save(path)
