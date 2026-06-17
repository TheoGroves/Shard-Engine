import os
import moderngl
import OpenEXR
import Imath
import numpy as np
from maths.matrices import get_view_matrix, get_projection_matrix, screen_to_world_ray
from collisions import raycast

shader_dir = "assets/shaders"

NORMAL_VISUALISER = False

with open(os.path.join(shader_dir, "standard.vert")) as f:
    VERT_SHADER = f.read()

with open(os.path.join(shader_dir, "standard.frag")) as f:
    FRAG_SHADER = f.read()


with open(os.path.join(shader_dir, "normal.vert")) as f:
    NORMAL_VERT_SHADER = f.read()

with open(os.path.join(shader_dir, "normal.frag")) as f:
    NORMAL_VISUALISER_SHADER = f.read()

class Renderer:
    def __init__(self, ctx: moderngl.Context, width: int, height:int):
        self.ctx = ctx
        self.ctx.enable(moderngl.CULL_FACE)
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.wireframe = False

        self.width = width
        self.height = height
        self.fov = 90.0
        self.near = 0.1
        self.far = 1000.0
        self.aspect = width / height
        self.camera = None

        self.proj = get_projection_matrix(self)
        self.view = None

        self.env_map = None

        self.program = None

    def set_camera(self, cam_transform, camera):
        self.cam_transform = cam_transform
        self.camera = camera
        self.view = get_view_matrix(cam_transform)

    def screen_to_world(self, screen_x, screen_y, grid, tris):
        origin, direction = screen_to_world_ray(screen_x, screen_y, (self.width, self.height), self.proj, self.view)
        return raycast(origin, direction, grid, tris)

    def generate_buffers(self, mesh_renderer):
        mesh_renderer.mesh.vbo = self.ctx.buffer(
            mesh_renderer.mesh.vertices.astype("f4").tobytes()
        )

        mesh_renderer.mesh.ibo = self.ctx.buffer(
            mesh_renderer.mesh.indices.astype("i4").tobytes()
        )

        mesh_renderer.mesh.vao = self.ctx.vertex_array(
            self.program,
            [
                (
                    mesh_renderer.mesh.vbo,
                    "3f 2f 3f 3f",
                    "in_pos",
                    "in_uv_map",
                    "in_normal",
                    "in_tangent"
                )
            ],
            mesh_renderer.mesh.ibo
        )

    def load_env_map(self, path):
        exr = OpenEXR.InputFile(path)
        dw = exr.header()['dataWindow']

        width = dw.max.x - dw.min.x + 1
        height = dw.max.y - dw.min.y + 1

        pt = Imath.PixelType(Imath.PixelType.FLOAT)

        r = np.frombuffer(exr.channel('R', pt), dtype=np.float32)
        g = np.frombuffer(exr.channel('G', pt), dtype=np.float32)
        b = np.frombuffer(exr.channel('B', pt), dtype=np.float32)

        img = np.stack([r, g, b], axis=-1)
        img = img.reshape((height, width, 3))
        img = np.flipud(img)

        self.env_map = self.ctx.texture(size=(width, height), components=3, data=img.tobytes(), dtype='f4')

    def build_pipeline(self):
        if not NORMAL_VISUALISER:
            self.program = self.ctx.program(
                vertex_shader=VERT_SHADER,
                fragment_shader=FRAG_SHADER
            )

        else:
            self.program = self.ctx.program(
                vertex_shader=NORMAL_VERT_SHADER,
                fragment_shader=NORMAL_VISUALISER_SHADER
            )