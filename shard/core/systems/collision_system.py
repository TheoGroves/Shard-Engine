import time
import os

from shard.collisions import raycast, solve_capsule

from ..entity import EntityManager
from ..asset_manager import AssetManager

from shard.collisions import BVH, Vec3, Mat4, get_world_triangles

class CollisionSystem:
    def __init__(self, entity_manager: EntityManager, asset_manager: AssetManager):
        self.entity_manager = entity_manager
        self.asset_manager = asset_manager
        self.triangles = None
        self.bvh = None
        self.rebuild_bvh = False

        self.old_entities = {}

    def get_collision_triangles(self, bvh: BVH):
        triangles = []

        for eid in self.entity_manager.query("MeshCollider", "Transform"):
            mc_entity = self.entity_manager.entities[eid]
            mesh_collider = mc_entity.components["MeshCollider"]
            transform = mc_entity.components["Transform"]

            verts = mesh_collider.mesh.vertices.reshape(-1, 11)[:, :3]
            vecs = [Vec3(*v) for v in verts]

            model = transform.model

            new = get_world_triangles(
                vecs,
                list(mesh_collider.mesh.indices),
                model
            )

            triangles.extend(new)

        bvh.build(triangles)
            
        self.triangles = triangles
        self.bvh = bvh

    def set_mesh(self, eid, mesh_path):
        _, mesh = self.asset_manager.get_mesh(mesh_path)
        collider = self.entity_manager.entities[eid].components["MeshCollider"]
        collider.mesh = mesh
        collider.path = mesh_path

    def update(self, engine):
        # Rebuild bvh when any uninitialized meshes have been created/meshes have been changed
        self.rebuild_bvh = False
        for eid in self.entity_manager.query("MeshCollider"):
            collider = self.entity_manager.entities[eid].components["MeshCollider"]
    
            # Compare new entities to old entities and find differences
            old_path = self.old_entities.get(eid)
            if old_path is not None and os.path.abspath(old_path) != os.path.abspath(collider.path):
                self.set_mesh(eid, collider.path)
                self.rebuild_bvh = True
                engine.logger.log_debug(f"Mesh collider path on entity {eid} changed from {os.path.abspath(old_path)} -> {os.path.abspath(collider.path)}")

            # Generate new meshes
            if collider.mesh is None and isinstance(collider.path, str):
                self.set_mesh(eid, collider.path)
                self.rebuild_bvh = True
                engine.logger.log_debug(f"Entity {eid}'s mesh collider was rebuilt.")


        if self.rebuild_bvh:
            s = time.perf_counter()
            engine.rebuild_bvh()
            engine.logger.log_debug(f"BVH Rebuilt in {(time.perf_counter()-s)*1000:.1f}ms")

        capsule_eids = self.entity_manager.query("CapsuleCollider", "Transform")

        for capsule_eid in capsule_eids:
            capsule_entity = self.entity_manager.entities[capsule_eid]

            transform = capsule_entity.components["Transform"]
            capsule   = capsule_entity.components["CapsuleCollider"]
            
            collision, normal = solve_capsule(transform, capsule, self.triangles, self.bvh)

            if "LinearBody" in capsule_entity.components:
                linear_body = capsule_entity.components["LinearBody"]

                if linear_body and collision and linear_body.velocity.y < 0:
                    linear_body.velocity.y = 0

        # Generate old entities dict for next frame to compare against
        self.old_entities = {}
        for eid in self.entity_manager.query("MeshCollider"):
            collider = self.entity_manager.entities[eid].components["MeshCollider"]
            self.old_entities[eid] = os.path.abspath(collider.path)