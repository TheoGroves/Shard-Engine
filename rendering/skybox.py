import numpy as np
import os

shader_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "shaders")

def generate_skybox(ctx, skybox_settings):
    cube_vertices = np.array([
        -1, -1, -1,
         1, -1, -1,
         1,  1, -1,
         1,  1, -1,
        -1,  1, -1,
        -1, -1, -1,
        -1, -1,  1,
         1, -1,  1,
         1,  1,  1,
         1,  1,  1,
        -1,  1,  1,
        -1, -1,  1,
        -1,  1,  1,
        -1,  1, -1,
        -1, -1, -1,
        -1, -1, -1,
        -1, -1,  1,
        -1,  1,  1,
         1,  1,  1,
         1,  1, -1,
         1, -1, -1,
         1, -1, -1,
         1, -1,  1,
         1,  1,  1,
        -1, -1, -1,
         1, -1, -1,
         1, -1,  1,
         1, -1,  1,
        -1, -1,  1,
        -1, -1, -1,
        -1,  1, -1,
         1,  1, -1,
         1,  1,  1,
         1,  1,  1,
        -1,  1,  1,
        -1,  1, -1,
    ], dtype='f4')

    shader = "proc_skybox.frag" if skybox_settings.procedural else "skybox.frag"

    with open(os.path.join(shader_dir, "skybox.vert")) as f:
        VERT_SHADER = f.read()

    with open(os.path.join(shader_dir, shader)) as f:
        FRAG_SHADER = f.read()

    prog = ctx.program(
        vertex_shader=VERT_SHADER,
        fragment_shader=FRAG_SHADER
    )

    vbo = ctx.buffer(cube_vertices.tobytes())

    vao = ctx.vertex_array(
        prog,
        [
            (vbo, "3f", "in_pos")
        ]
    )

    return vao, prog

class SkyboxSettings:
    def __init__(self, procedural, sun_dir, sun_col):
        self.procedural = procedural
        self.sun_dir = sun_dir
        self.sun_col = sun_col