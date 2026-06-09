import numpy as np
from core.mesh import Mesh
from maths.matrices import get_model_matrix
from loaders.obj_parser import parse_obj, build_interleaved

class Collider:
    def __init__(self, ctx, mesh_path, debug=False):
        self.ctx = ctx
        self.mesh_path = mesh_path

        self.debug = debug

        self.mesh = Mesh()

        self.model_matrix = None

        self.load_mesh()

    def load_mesh(self):
        verts, norms, tans, bitans, uvs, inds, n_inds, uv_inds = parse_obj(self.mesh_path)

        self.mesh.vertices, self.mesh.indices = build_interleaved(
            verts, norms, tans, bitans, uvs,
            inds, n_inds, uv_inds
        )

        self.mesh.vbo = self.ctx.buffer(self.mesh.vertices.astype("f4").tobytes())
        self.mesh.ibo = self.ctx.buffer(self.mesh.indices.astype("i4").tobytes())

    def build_debug_vao(self, prog):
        self.mesh.vao = self.ctx.vertex_array(
            prog,
            [
                (self.mesh.vbo, "3f 32x", "in_pos")
            ],
            self.mesh.ibo
        )

    def set_model(self, transform):
        self.model_matrix = get_model_matrix(transform.pos, transform.rot, transform.scale)

    def get_world_triangles(self):
        verts = self.mesh.vertices.reshape(-1, 11)

        model = self.model_matrix

        tris = []

        for i in range(0, len(self.mesh.indices), 3):
            i0 = self.mesh.indices[i]
            i1 = self.mesh.indices[i + 1]
            i2 = self.mesh.indices[i + 2]

            p0 = verts[i0][:3]
            p1 = verts[i1][:3]
            p2 = verts[i2][:3]

            p0 = (model @ np.array([*p0,1]))[:3]
            p1 = (model @ np.array([*p1,1]))[:3]
            p2 = (model @ np.array([*p2,1]))[:3]

            tris.append((p0,p1,p2))

        return tris