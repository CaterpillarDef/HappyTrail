
class Node:
    def __init__(self, elevation, x, y):
        self.cost = elevation
        self.pos = (x, y)
        self.edges = {}  # {(dx, dy): shift}
        self.mines = False
        self.enemy = False

    def get_cost(self):
        return self.cost if not self.mines and not self.enemy else float('inf')
    def set_cost(self, change):
        self.cost += change
    def get_pos(self):
        return self.pos
    def get_edges(self):
        return self.edges
