import numpy as np
from maths.matrices import get_model_matrix
from loaders.obj_parser import parse_obj, build_interleaved

class Collider:
    def __init__(self, ctx, mesh_path, debug=False):
        self.ctx = ctx
        self.mesh_path = mesh_path

        self.debug = debug

        self.vertices = None
        self.indices = None

        self.vbo = None
        self.ibo = None
        self.vao = None

        self.model_matrix = None

        self.load_mesh()

    def load_mesh(self):
        verts, norms, tans, bitans, uvs, inds, n_inds, uv_inds = parse_obj(self.mesh_path)

        self.vertices, self.indices = build_interleaved(
            verts, norms, tans, bitans, uvs,
            inds, n_inds, uv_inds
        )

        self.vbo = self.ctx.buffer(self.vertices.astype("f4").tobytes())
        self.ibo = self.ctx.buffer(self.indices.astype("i4").tobytes())

    def build_debug_vao(self, prog):
        self.vao = self.ctx.vertex_array(
            prog,
            [
                (self.vbo, "3f 32x", "in_pos")
            ],
            self.ibo
        )

    def set_model(self, transform):
        self.model_matrix = get_model_matrix(transform.pos, transform.rot, transform.scale)

    def get_world_triangles(self):
        verts = self.vertices.reshape(-1, 11)

        model = self.model_matrix

        tris = []

        for i in range(0, len(self.indices), 3):
            i0 = self.indices[i]
            i1 = self.indices[i + 1]
            i2 = self.indices[i + 2]

            p0 = verts[i0][:3]
            p1 = verts[i1][:3]
            p2 = verts[i2][:3]

            p0 = (model @ np.array([*p0,1]))[:3]
            p1 = (model @ np.array([*p1,1]))[:3]
            p2 = (model @ np.array([*p2,1]))[:3]

            tris.append((p0,p1,p2))

        return tris