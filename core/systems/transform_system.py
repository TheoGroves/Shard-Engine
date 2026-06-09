import numpy as np
from ecs import EntityManager
from maths.matrices import get_model_matrix

def normalize(v):
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / n

class TransformSystem:
    def __init__(self, em: EntityManager):
        self.em = em
        self.world_up = np.array([0, 1, 0], dtype=np.float32)

    def set_pos(self, eid, pos):
        t=self.em.entities[eid].components["Transform"]
        t.pos = pos
        self.update_model_matrix(t)

    def set_rot(self, eid, rot):
        t=self.em.entities[eid].components["Transform"]
        t.rot = rot
        self.update_model_matrix(t)

    def set_scale(self, eid, scale):
        t=self.em.entities[eid].components["Transform"]
        t.scale = scale
        self.update_model_matrix(t)

    def get_transform(self, eid):
        return self.em.entities[eid].components["Transform"]

    def update_model_matrix(self, t):
        t.model = get_model_matrix(t.pos, t.rot, t.scale)

    def update(self):
        for eid in self.em.query("Transform"):
            transform = self.em.entities[eid].components["Transform"]

            yaw_rad = np.radians(transform.rot[1])
            pitch_rad = np.radians(transform.rot[0])

            front = np.array([
                np.cos(yaw_rad) * np.cos(pitch_rad),
                np.sin(pitch_rad),
                np.sin(yaw_rad) * np.cos(pitch_rad)
            ], dtype=np.float32)

            transform.front = normalize(front)
            transform.right = normalize(np.cross(transform.front, self.world_up))
            transform.up = normalize(np.cross(transform.front, transform.right))