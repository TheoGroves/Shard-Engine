import time
import numpy as np
import spatial_collision_engine as sce
from ecs import EntityManager
from loaders.obj_parser import parse_objs, build_interleaved
from core.mesh import Mesh
from core.renderer import Renderer
from core.asset_manager import AssetManager


class MeshColliderSystem:
    def __init__(self, em: EntityManager, renderer: Renderer, asset_manager: AssetManager):
        self.em = em
        self.renderer = renderer
        self.asset_manager = asset_manager

    def load_model(self, eid, path):
        mesh_collider = self.em.entities[eid].components["MeshCollider"]

        mesh_collider.mesh = self.asset_manager.get_mesh(path)

        self.renderer.generate_buffers(mesh_collider)

    def build_debug_vao(self, eid, prog, ctx):
        mc = self.em.entities[eid].components["MeshCollider"]

        mc.mesh.vao = ctx.vertex_array(
            prog,
            [
                (mc.mesh.vbo, "3f 32x", "in_pos")
            ],
            mc.mesh.ibo
        )
    
    def get_collision_triangles(self, bvh):
        triangles = []

        for eid in self.em.query("MeshCollider", "Transform"):
            mc_entity = self.em.entities[eid]
            mesh_collider = mc_entity.components["MeshCollider"]
            transform = mc_entity.components["Transform"]

            verts = mesh_collider.mesh.vertices.reshape(-1, 11)[:, :3]
            vecs = [sce.Vec3(*v) for v in verts]

            model = transform.model.flatten()

            new = sce.get_world_triangles(
                vecs,
                list(mesh_collider.mesh.indices),
                sce.Mat4(list(model))
            )

            triangles.extend(new)

        bvh.build(triangles)
            
        return triangles