class Mesh:
    def __init__(self, vertices=None, indices=None, vbo=None, ibo=None, vao=None, shadow_vao=None):
        self.vertices = vertices
        self.indices = indices

        self.vbo = vbo
        self.ibo = ibo
        self.vao = vao

        self.shadow_vao = shadow_vao