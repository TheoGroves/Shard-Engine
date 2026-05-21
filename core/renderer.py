import os
import moderngl
from maths.matrices import get_view_matrix, get_projection_matrix
from core.camera import Camera
from core.game_object import GameObject
from core.scene import Scene

shader_dir = "assets/shaders"

with open(os.path.join(shader_dir, "standard.vert")) as f:
    VERT_SHADER = f.read()

with open(os.path.join(shader_dir, "standard.frag")) as f:
    FRAG_SHADER = f.read()


class Renderer:
    def __init__(self, ctx: moderngl.Context, width: int, height:int, camera: Camera):
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
        self.camera = camera

        self.proj = get_projection_matrix(self)
        self.view = get_view_matrix(camera)

        self.program = None

    def load_mesh(self, game_object: GameObject):
        game_object.vbo = self.ctx.buffer(
            game_object.vertices.astype("f4").tobytes()
        )

        game_object.ibo = self.ctx.buffer(
            game_object.indices.astype("i4").tobytes()
        )

        game_object.vao = self.ctx.vertex_array(
            self.program,
            [
                (
                    game_object.vbo,
                    "3f 2f 3f 3f",
                    "in_pos",
                    "in_uv_map",
                    "in_normal",
                    "in_tangent"
                )
            ],
            game_object.ibo
        )

    def build_pipeline(self):
        self.program = self.ctx.program(
            vertex_shader=VERT_SHADER,
            fragment_shader=FRAG_SHADER
        )

        self.program["light_dir"].value = (0.0, 1.0, 1.0)
        self.program["cam_pos"].value = tuple(self.camera.position)

    def render(self, scene: Scene):
        self.ctx.clear(0.05, 0.05, 0.08, 1.0)
        self.ctx.clear(depth=1.0)

        self.view = get_view_matrix(self.camera)
        for game_object in scene.game_objects:
            self.program["model"].write(game_object.model.astype("f4").T.tobytes())
            self.program["view"].write(self.view.astype("f4").T.tobytes())
            self.program["proj"].write(self.proj.astype("f4").T.tobytes())
            self.program["cam_pos"].value = tuple(self.camera.position)
            self.program["roughness"].value = game_object.material.roughness

            if game_object.material.texture:
                game_object.material.texture.use(location=0)
                self.program["tex"] = 0

            if game_object.material.normal_map:
                game_object.material.normal_map.use(location=1)
                self.program["normal_map"] = 1

            game_object.vao.render()