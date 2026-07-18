from collisions import raycast, solve_capsule

from ..entity import EntityManager
from ..asset_manager import AssetManager

from collisions import BVH, Vec3, Mat4, get_world_triangles

class CollisionSystem:
    def __init__(self, entity_manager: EntityManager, asset_manager: AssetManager):
        self.entity_manager = entity_manager
        self.asset_manager = asset_manager
        self.triangles = None
        self.bvh = None

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

    def update(self):
        capsule_eids = self.entity_manager.query("CapsuleCollider", "Transform")

        for capsule_eid in capsule_eids:
            capsule_entity = self.entity_manager.entities[capsule_eid]

            transform = capsule_entity.components["Transform"]
            capsule   = capsule_entity.components["CapsuleCollider"]
            
            collision, normal = solve_capsule(transform, capsule, self.triangles, self.bvh)

            linear_body = capsule_entity.components["LinearBody"]

            if linear_body and collision and linear_body.velocity.y < 0:
                linear_body.velocity.y = 0