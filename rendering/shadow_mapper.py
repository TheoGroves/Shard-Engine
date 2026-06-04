import moderngl
import numpy as np

from maths.matrices import look_at, orthographic

class ShadowMapper:
    def __init__(self, ctx, light_dir, shadow_size=2048):
        self.ctx = ctx
        self.light_dir = np.array(light_dir, dtype=np.float32)

        self.shadow_size = shadow_size

        self.depth_tex = ctx.depth_texture((shadow_size, shadow_size))
        self.depth_tex.repeat_x = False
        self.depth_tex.repeat_y = False

        self.fbo = ctx.framebuffer(depth_attachment=self.depth_tex)

        self.light_proj = orthographic(
            -40, 40,
            -40, 40,
            0.1, 50.0
        )

        light_pos = -self.light_dir * 20.0

        self.light_view = look_at(
            light_pos,
            np.array([0,0,0], dtype=np.float32),
            np.array([0,1,0], dtype=np.float32)
        )

        self.light_space_matrix = self.light_proj @ self.light_view

        with open("assets/shaders/shadow.vert") as f:
            vert = f.read()

        with open("assets/shaders/shadow.frag") as f:
            frag = f.read()

        self.program = ctx.program(
            vertex_shader=vert,
            fragment_shader=frag
        )

    def generate_shadow_vao(self, game_object):
        game_object.shadow_vao = self.ctx.vertex_array(
            self.program,
            [
                (
                    game_object.vbo,
                    "3f 2f 24x",
                    "in_pos",
                    "in_uv_map"
                )
            ],
            game_object.ibo
        )

    def render_depth(self, scene):
        self.fbo.use()

        self.ctx.viewport = (
            0,
            0,
            self.shadow_size,
            self.shadow_size
        )

        self.ctx.clear(depth=1.0)

        for obj in scene.game_objects:
            self.program["model"].write(
                obj.model.astype("f4").T.tobytes()
            )

            self.program["light_space"].write(
                self.light_space_matrix.astype("f4").T.tobytes()
            )

            if obj.material.texture:
                obj.material.texture.use(location=0)
                self.program["tex"] = 0

            obj.shadow_vao.render()

        self.ctx.screen.use()

    def update(self, camera):
        target = camera.position.astype(np.float32)

        light_pos = target - self.light_dir * 20.0

        self.light_view = look_at(
            light_pos,
            target,
            np.array([0, 1, 0], dtype=np.float32)
        )

        self.light_space_matrix = self.light_proj @ self.light_view