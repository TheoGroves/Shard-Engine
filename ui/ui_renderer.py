import moderngl
from maths.matrices import get_screen_projection

class UIRenderer:
    def __init__(self, ctx: moderngl.Context, screen_size):
        self.ctx = ctx
        self.width = screen_size[0]
        self.height = screen_size[1]
        self.ortho = get_screen_projection(self.width, self.height)

        with open("assets/shaders/ui.vert") as f:
            vert = f.read()

        with open("assets/shaders/ui.frag") as f:
            frag = f.read()

        self.program = ctx.program(
            vertex_shader=vert,
            fragment_shader=frag
        )

        self.program["proj"].write(
            self.ortho.astype("f4").T.tobytes()
        )

        self.elements = []

    def add_quad(self, element):
        element.screen_size = (self.width, self.height)
        element.update_vertices()

        element.vbo = self.ctx.buffer(element.vertices.astype("f4").tobytes())
        element.vao = self.ctx.vertex_array(
            self.program,
            [
                (element.vbo, "2f 2f", "in_pos", "in_uv")
            ]
        )

        self.elements.append(element)

    def get_quad(self, index):
        return self.elements[index]
    
    def check_ui_blocking(self):
        return any(quad.is_blocking() for quad in self.elements)

    def render(self):
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.disable(moderngl.CULL_FACE)
        self.ctx.depth_mask = False
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        for quad in self.elements:
            quad.tex.use(location=0)
            self.program["tex"] = 0
            quad.vao.render()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)
        self.ctx.depth_mask = True
        self.ctx.disable(moderngl.BLEND)