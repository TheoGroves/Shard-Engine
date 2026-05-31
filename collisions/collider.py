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