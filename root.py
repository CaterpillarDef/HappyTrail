import networkx as nx
import numpy as np
import pandas as pd

from loader import load_terrain_data
from heatmap_tools import normalize_heatmap

class PathHandler:
    def __init__(self, elevation_data_file,water_data_file):
        self.elevation_data = normalize_heatmap(load_terrain_data(elevation_data_file))
        self.water_data = normalize_heatmap(load_terrain_data(water_data_file, invert=True)).map(lambda v: v * 10)
        # swamp self.swamp_data = normalize_heatmap(load_terrain_data(swamp_data_file, invert=True))
        # boulders self.boulder_data = normalize_heatmap(load_terrain_data(boulder_data_file, invert=True))
        self.path_cost = normalize_heatmap(self.elevation_data.where(self.water_data > 0, self.water_data))
        print(self.elevation_data.shape)

    def generate_pathlets(self):
        height, width = self.path_cost.shape

        graph = nx.Graph()

        for y in range(height):
            for x in range(width):
                node_id = (x, y)
                graph.add_node(node_id, cost=self.path_cost.iloc[y, x])
        directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

        for y in range(height):
            for x in range(width):
                current_node = (x, y)
                current_value = self.path_cost.iloc[y, x]

                for dx, dy in directions:
                    n_x, n_y = x + dx, y + dy

                    if 0 <= n_x < width and 0 <= n_y < height:
                        neighbor_node = (n_x, n_y)
                        neighbor_value = self.path_cost.iloc[n_y, n_x]

                        # diag = 1 if abs(dx) + abs(dy) == 1 else (2**0.5)
                        edge_weight = abs(current_value - neighbor_value) # ((current_value + neighbor_value) / 2.0) * diag
                        graph.add_edge(current_node, neighbor_node, weight=float(edge_weight))
        #print(graph.number_of_edges())
        return graph

    def _prime_path(self):
        self.path_graph = self.generate_pathlets()
        self.path_overlay = pd.DataFrame(np.full(self.elevation_data.shape, fill_value=0))

    def find_best_path(self, infil=None, target=None):
        if self.infil_zone is None and infil is None:
            raise ValueError("Infiltration zone not set.")
            return None
        if self.target_zone is None and target is None:
            raise ValueError("Target zone not set.")
            return None
        self._prime_path()

        source = infil or self.infil_zone
        target = target or self.target_zone

        print(f"Finding path from {source} to {target}")
        print(f"Map dimensions: {self.path_cost.shape}")

        try:
            path = nx.shortest_path(self.path_graph, source=source, target=target, weight='weight')
            print(f"Path found with {len(path)} points")
            print(f"First few points: {path[:5]}")
            print(f"Last few points: {path[-5:]}")

            total_cost = nx.shortest_path_length(self.path_graph, source=source, target=target, weight='weight')
            self.path_overlay[:] = 1
            for (x, y) in path:
                if 0 <= y < self.path_overlay.shape[0] and 0 <= x < self.path_overlay.shape[1]:
                    self.path_overlay.iloc[y, x] = 0
                    total_cost += self.path_cost.iloc[y, x]
            return path, float(total_cost)
        except nx.NetworkXNoPath:
            print(f"No path exists between {source} and {target}")
            return None, float('inf')
        except Exception as e:
            print(f"Error finding path: {e}")
            return None, float('inf')

    def export_heatmap(self):
        from export_mapping import export_heatmap, export_heatmap_with_path
        export_heatmap(self.path_cost, "heatmaps/path_cost_heatmap.png")
        export_heatmap(self.path_overlay, "heatmaps/path_overlay.png")
        export_heatmap_with_path(self.path_cost, self.path_overlay, "heatmaps/combined_path_map.png", 'green')

    def set_infil(self, x, y):
        self.infil_zone = (x, y)

    def set_target(self, x, y):
        if x < 0 or y < 0 or x >= self.path_cost.shape[1] or y >= self.path_cost.shape[0]:
            raise ValueError("Target coordinates out of bounds.")
            return None
        self.target_zone = (x, y)

    def set_exfil(self, x, y):
        self.exfil_zone = (x, y)

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
        path_handler.set_infil(5,5)
        path_handler.set_target(980,450)
        print(path_handler.find_best_path())
        path_handler.export_heatmap()
