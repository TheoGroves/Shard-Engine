import numpy as np
from ecs import EntityManager
from loaders.obj_parser import parse_objs, build_interleaved
from core.mesh import Mesh
from core.renderer import Renderer

class MeshColliderSystem:
    def __init__(self, em: EntityManager, renderer: Renderer):
        self.em = em
        self.renderer = renderer

    def load_model(self, eid, path):
        mesh_collider = self.em.entities[eid].components["MeshCollider"]

        mesh_collider.model_path = path
        vertex_buffer, normal_buffer, tangent_buffer, bitangent_buffer, uv_buffer, index_buffer, normal_index_buffer, uv_index_buffer = parse_objs([path])

        mesh_collider.mesh = Mesh()

        mesh_collider.mesh.vertices, mesh_collider.mesh.indices = build_interleaved(
            vertex_buffer,
            normal_buffer,
            tangent_buffer,
            bitangent_buffer,
            uv_buffer,
            index_buffer,
            normal_index_buffer,
            uv_index_buffer
        )

        self.renderer.generate_buffers(mesh_collider)

    def build_debug_vao(self, eid, prog):
        mc = self.em.entities[eid].components["MeshCollider"]
        mc.mesh.vao = self.ctx.vertex_array(
            prog,
            [
                (mc.mesh.vbo, "3f 32x", "in_pos")
            ],
            mc.mesh.ibo
        )

    def get_world_triangles(self, eid):
        mc_entity = self.em.entities[eid]
        mesh_collider = mc_entity.components["MeshCollider"]
        transform = mc_entity.components["Transform"]

        verts = mesh_collider.mesh.vertices.reshape(-1, 11)

        model = transform.model

        tris = []

        for i in range(0, len(mesh_collider.mesh.indices), 3):
            i0 = mesh_collider.mesh.indices[i]
            i1 = mesh_collider.mesh.indices[i + 1]
            i2 = mesh_collider.mesh.indices[i + 2]

            p0 = verts[i0][:3]
            p1 = verts[i1][:3]
            p2 = verts[i2][:3]

            p0 = (model @ np.array([*p0,1]))[:3]
            p1 = (model @ np.array([*p1,1]))[:3]
            p2 = (model @ np.array([*p2,1]))[:3]

            tris.append((p0,p1,p2))

        return tris
    
    def get_collision_triangles(self, grid):
        triangles = []

        for eid in self.em.query("MeshCollider", "Transform"):
            for tri in self.get_world_triangles(eid):
                idx = len(triangles)

                triangles.append(tri)

                a,b,c = tri

                grid.insert_triangle(
                    idx,
                    a,b,c
                )
            
        return triangles