import numpy as np
from collections import defaultdict

class SpatialGrid:
    def __init__(self, cell_size=2.0):
        self.cell_size = cell_size
        self.cells = defaultdict(list)

    def clear(self):
        self.cells.clear()

    def world_to_cell(self, p):
        return (
            int(np.floor(p[0] / self.cell_size)),
            int(np.floor(p[1] / self.cell_size)),
            int(np.floor(p[2] / self.cell_size))
        )

    def insert_triangle(self, tri_index, a, b, c):
        mins = np.minimum(np.minimum(a, b), c)
        maxs = np.maximum(np.maximum(a, b), c)

        min_cell = self.world_to_cell(mins)
        max_cell = self.world_to_cell(maxs)

        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                for z in range(min_cell[2], max_cell[2] + 1):
                    self.cells[(x, y, z)].append(tri_index)

    def query_capsule(self, mins, maxs):
        result = set()

        min_cell = self.world_to_cell(mins)
        max_cell = self.world_to_cell(maxs)

        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                for z in range(min_cell[2], max_cell[2] + 1):
                    result.update(
                        self.cells.get((x, y, z), [])
                    )

        return result