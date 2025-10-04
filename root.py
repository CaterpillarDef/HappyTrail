
from loader import load_terrain_data
from heatmap_tools import normalize_heatmap

class PathHandler:
    def __init__(self, elevation_data_file,water_data_file):
        elevation_data = normalize_heatmap(load_terrain_data(elevation_data_file))
        water_data = normalize_heatmap(load_terrain_data(water_data_file, invert=True))
        self.path_cost = normalize_heatmap(elevation_data.where(water_data > 0, water_data))
        from export_mapping import export_heatmap
        export_heatmap(elevation_data, "heatmaps/elevation_heatmap.png")
        export_heatmap(water_data, "heatmaps/water_heatmap.png")
        export_heatmap(self.path_cost, "heatmaps/path_cost_heatmap.png")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 0 and sys.argv[1] == 'dev':
        from random_terrain import create_terrain, save_terrain_grayscale
        desired_size = 1024
        output_file = "./greyscale_terrain.png"
        terrain_nodes = create_terrain(desired_size)
        save_terrain_grayscale(terrain_nodes, output_file, invert=False)
    elif len(sys.argv) > 0 and sys.argv[1] == 'run':
        elevation_file = 'elevation.png'
        water_file = 'water.png'
        path_handler = PathHandler(elevation_file, water_file)
