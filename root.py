
import networkx as nx

from loader import load_terrain_data
from heatmap_tools import normalize_heatmap

class PathHandler:
    def __init__(self, elevation_data_file,water_data_file):
        self.elevation_data = normalize_heatmap(load_terrain_data(elevation_data_file))
        self.water_data = normalize_heatmap(load_terrain_data(water_data_file, invert=True))
        # swamp self.swamp_data = normalize_heatmap(load_terrain_data(swamp_data_file, invert=True))
        # boulders self.boulder_data = normalize_heatmap(load_terrain_data(boulder_data_file, invert=True))

    def generate_heatmap(self):
        path_cost = normalize_heatmap(self.elevation_data.where(self.water_data > 0, self.water_data))
        return path_cost

    def generate_pathlets(self):
        heatmap = self.generate_heatmap()
        height, width = heatmap.shape

        graph = nx.Graph()

        for y in range(height):
            for x in range(width):
                node_id = (x, y)
                graph.add_node(node_id, cost=heatmap.iloc[y, x])
        directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

        for y in range(height):
            for x in range(width):
                current_node = (x, y)
                current_value = heatmap.iloc[y, x]

                for dx, dy in directions:
                    n_x, n_y = x + dx, y + dy

                    if 0 <= n_x < width and 0 <= n_y < height:
                        neighbor_node = (n_x, n_y)
                        neighbor_value = heatmap.iloc[n_y, n_x]

                        edge_weight = abs(current_value - neighbor_value)
                        graph.add_edge(current_node, neighbor_node, weight=edge_weight)
        print(graph.number_of_edges())
        return graph

    def export_heatmap(self):
        from export_mapping import export_heatmap
        export_heatmap(self.generate_heatmap(), "heatmaps/path_cost_heatmap.png")

    def set_infil(self, x, y):
        self.infil_zone = (x, y)

    def set_target(self, x, y):
        self.target_zone = (x, y)

    def set_exfil(self, x, y):
        self.exfil_zone = (x, y)

    def find_best_path(self):
        pass

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
        path_handler.generate_pathlets()
