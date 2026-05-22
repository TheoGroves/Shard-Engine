import numpy as np
import os

shader_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "shaders")

with open(os.path.join(shader_dir, "skybox.vert")) as f:
    VERT_SHADER = f.read()

with open(os.path.join(shader_dir, "skybox.frag")) as f:
    FRAG_SHADER = f.read()

def generate_skybox(ctx):
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