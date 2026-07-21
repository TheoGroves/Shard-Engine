from ..component import component
from shard_maths import Vec3, model_matrix

@component
class Transform:
    def __init__(self, pos: Vec3, rot: Vec3, scale: Vec3):
        self.pos = pos
        self.rot = rot
        self.scale = scale

        self.world_pos = pos

        self.forward = Vec3(0,0,1)
        self.right = Vec3(1,0,0)
        self.up = Vec3(0,1,0)

        self.world_forward = Vec3(0,0,1)
        self.world_right = Vec3(1,0,0)
        self.world_up = Vec3(0,1,0)

        self.model = model_matrix(pos, rot, scale)
        self.world = model_matrix(pos, rot, scale)

        self.parent = None