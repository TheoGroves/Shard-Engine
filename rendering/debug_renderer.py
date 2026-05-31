import moderngl

class ColliderDebugger:
    def __init__(self, ctx):
        self.ctx = ctx

        with open("assets/shaders/debug.vert") as f:
            debug_vert = f.read()

        with open("assets/shaders/debug.frag") as f:
            debug_frag = f.read()

        self.program = self.ctx.program(
            vertex_shader=debug_vert,
            fragment_shader=debug_frag
        )

    def draw(self, renderer, colliders):
        if not self.program:
            return

        self.program["view"].write(renderer.view.astype("f4").T.tobytes())
        self.program["proj"].write(renderer.proj.astype("f4").T.tobytes())

        self.ctx.wireframe = True

        for c in colliders:
            if not c.debug:
                continue

            c.build_debug_vao(self.program)

            self.program["model"].write(
                c.model_matrix.astype("f4").T.tobytes()
            )

            c.vao.render()

        self.ctx.wireframe = False