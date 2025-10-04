
def normalize_heatmap(heatmap):
    min_val = heatmap.min(axis=None)
    max_val = heatmap.max(axis=None)

    if max_val - min_val == 0:
        return heatmap - min_val  # Avoid division by zero if all values are the same

    normalized_heatmap = (heatmap - min_val) / (max_val - min_val)
    return normalized_heatmap
