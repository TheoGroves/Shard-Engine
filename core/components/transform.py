import numpy as np
from ecs import component
from maths.matrices import get_model_matrix

@component
class Transform:
    def __init__(self, pos=np.array([0, 0, 0], dtype=np.float32), rot=np.array([0, 0, 0], dtype=np.float32), scale=np.array([1, 1, 1], dtype=np.float32)):
        self.pos = pos
        self.rot = rot
        self.scale = scale
        self.front = np.array([0, 0, -1], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.array([1, 0, 0], dtype=np.float32)
        self.model = get_model_matrix(self.pos, self.rot, self.scale)

        self.world_up = np.array([0, 1, 0], dtype=np.float32)

    @staticmethod
    def identity():
        return Transform((0,0,0), (0,0,0), (1,1,1))