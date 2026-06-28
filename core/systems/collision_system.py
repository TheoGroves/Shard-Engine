from ecs import EntityManager
from collisions.collision_solver import solve_capsule

class CollisionSystem:
    def __init__(self, em: EntityManager):
        self.em = em

    def update(self, triangles, bvh):
        for eid in self.em.query("CapsuleCollider", "PlayerController"):
            player_entity = self.em.entities[eid]
            
            transform = player_entity.components["Transform"]
            capsule = player_entity.components["CapsuleCollider"]
            player_controller = player_entity.components["PlayerController"]
            player_controller.grounded, normal = solve_capsule(
                transform,
                capsule,
                triangles,
                bvh
            )