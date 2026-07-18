from ..entity import EntityManager
from core.logger import *

class PhysicsSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def update(self, gravity, dt):
        for eid in self.entity_manager.query("LinearBody"):
            physics_object = self.entity_manager.entities[eid]

            linear_body = physics_object.components["LinearBody"]
            transform = physics_object.components["Transform"]

            linear_body.velocity.y += gravity * dt
            linear_body.velocity *= 0.99
            transform.pos += linear_body.velocity * dt
