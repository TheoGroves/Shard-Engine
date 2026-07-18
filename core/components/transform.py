from ..component import component
from shard_maths import Vec3, model_matrix

@component
class Transform:
    def __init__(self, pos: Vec3, rot: Vec3, scale: Vec3):
        self.pos = pos
        self.rot = rot
        self.scale = scale

        self.world_up = Vec3(0,1,0)

        self.forward = Vec3(0,0,0)
        self.right = Vec3(0,0,0)
        self.up = Vec3(0,0,0)

        self.model = model_matrix(pos, rot, scale)