import os
import moderngl
from matrices import  get_model_matrix, get_view_matrix,get_projection_matrix
from camera import Camera

shader_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shaders")

with open(os.path.join(shader_dir, "standard.vert")) as f:
    VERT_SHADER = f.read()

with open(os.path.join(shader_dir, "standard.frag")) as f:
    FRAG_SHADER = f.read()


class Renderer:
    def __init__(self, ctx: moderngl.Context, width: int, height:int, camera: Camera):
        self.ctx = ctx
        self.ctx.enable(moderngl.CULL_FACE)
        ctx.enable(moderngl.DEPTH_TEST)
        #self.ctx.front_face = "ccw"
        #self.ctx.cull_face = "back"
        self.ctx.wireframe = False

        self.width = width
        self.height = height
        self.fov = 90.0
        self.near = 0.1
        self.far = 1000.0
        self.aspect = width / height
        self.camera = camera

        self.proj = get_projection_matrix(self)
        self.view = get_view_matrix(camera)
        self.model = get_model_matrix((0, 0, 0))

        self.program = None

    def load_mesh(self, vertices, indices):
        self.vbo = self.ctx.buffer(vertices.astype("f4").tobytes())
        self.ibo = self.ctx.buffer(indices.astype("i4").tobytes())
        self.index_count = len(indices)
        print(f"Mesh loaded: {len(vertices) // 8} vertices, {self.index_count} indices")

    def build_pipeline(self):
        self.program = self.ctx.program(
            vertex_shader=VERT_SHADER,
            fragment_shader=FRAG_SHADER
        )

        self.program["light_dir"].value = (0.0, 1.0, 1.0)
        self.program["shininess"].value = 32.0
        self.program["cam_pos"].value = tuple(self.camera.position)

        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (self.vbo, "3f 2f 3f 3f", "in_pos", "in_uv_map", "in_normal", "in_tangent")
            ],
            self.ibo
        )

    def render(self):
        self.ctx.clear(0.05, 0.05, 0.08, 1.0)
        self.ctx.clear(depth=1.0)

        self.view = get_view_matrix(self.camera)
        self.program["model"].write(self.model.astype("f4").T.tobytes())
        self.program["view"].write(self.view.astype("f4").T.tobytes())
        self.program["proj"].write(self.proj.astype("f4").T.tobytes())
        self.program["cam_pos"].value = tuple(self.camera.position)

        self.vao.render()