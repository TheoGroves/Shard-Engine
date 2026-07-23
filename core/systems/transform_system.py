from ..entity import EntityManager
from shard_maths import Vec3, Mat4, model_matrix, normalize, cross, radians
from rendering import forward_from_euler

class TransformSystem:
    def __init__(self, em: EntityManager, logger):
        self.em = em
        self.world_up = Vec3(0, 1, 0)
        self.logger = logger

    def set_pos(self, eid, pos: Vec3):
        t=self.em.entities[eid].components["Transform"]
        t.pos = pos

    def set_rot(self, eid, rot: Vec3):
        t=self.em.entities[eid].components["Transform"]
        t.rot = rot

    def set_scale(self, eid, scale: Vec3):
        t=self.em.entities[eid].components["Transform"]
        t.scale = scale

    def get_transform(self, eid):
        return self.em.entities[eid].components["Transform"]

    def set_parent(self, eid, t):
        child = self.em.entities[eid].components["Transform"]
        
        if child is t:
            self.logger.log_warning("Cannot parent transform to itself.")
            return 

        if child.parent is t:
            return

        if child.parent is not None:
            child.parent.children.remove(child)
        
        child.parent = t
        t.children.append(child)

    def update_model_matrix(self, t):
        t.model = model_matrix(t.pos, radians(t.rot), t.scale)

    def resolve_transform(self, eid):
        # Traverse up tree to root node and store transforms in chain
        t = self.em.entities[eid].components["Transform"]
        initial = t

        chain = []

        while t is not None:
            chain.append(t)
            t = t.parent

        # Iterate back down through reversed chain and apply transforms
        world = Mat4.identity()

        for t in reversed(chain):
            world = world * t.model

        initial.world = world
        
    def update(self):
        for eid in self.em.query("Transform"):
            transform = self.get_transform(eid)
            self.update_model_matrix(transform)

        for eid in self.em.query("Transform"):
            self.resolve_transform(eid)

        for eid in self.em.query("Transform"):
            transform = self.get_transform(eid)

            transform.world_forward = normalize(Vec3(transform.world.m[8], transform.world.m[9], transform.world.m[10]))
            transform.world_right   = normalize(Vec3(-transform.world.m[0], -transform.world.m[1], -transform.world.m[2])) # FIXME: inverted x axis due to coordinate mismatch
            transform.world_up      = normalize(Vec3(transform.world.m[4], transform.world.m[5], transform.world.m[6]))

            transform.world_pos     = Vec3(transform.world.m[12], transform.world.m[13], transform.world.m[14])