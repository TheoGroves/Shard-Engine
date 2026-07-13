from ..component import component
from shard_maths import Vec3, model_matrix

@component
class Transform:
    def __init__(self, pos: Vec3, rot: Vec3, scale: Vec3):
        self.pos = pos
        self.rot = rot
        self.scale = scale

        self.model = model_matrix(pos, rot, scale)