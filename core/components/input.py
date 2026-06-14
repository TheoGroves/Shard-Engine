import numpy as np
from ecs import component

@component
class Input:
    def __init__(self):
        self.keys = {}
        self.move_direction = np.zeros(3, dtype=np.float32)

    def serialize(self):
        return {}
    
    @classmethod
    def deserialize(cls, data, ctx):
        return cls()