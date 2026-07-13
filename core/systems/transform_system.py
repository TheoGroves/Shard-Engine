from ..entity import EntityManager
from shard_maths import Vec3, model_matrix

class TransformSystem:
    def __init__(self, em: EntityManager):
        self.em = em
        self.world_up = Vec3(0, 1, 0)

    def set_pos(self, eid, pos: Vec3):
        t=self.em.entities[eid].components["Transform"]
        t.pos = pos

    def set_rot(self, eid, rot: Vec3):
        t=self.em.entities[eid].components["Transform"]
        t.rot = rot
        self.update_model_matrix(t)

    def set_scale(self, eid, scale: Vec3):
        t=self.em.entities[eid].components["Transform"]
        t.scale = scale
        self.update_model_matrix(t)

    def get_transform(self, eid):
        return self.em.entities[eid].components["Transform"]

    def update_model_matrix(self, t):
        t.model = model_matrix(t.pos, t.rot, t.scale)