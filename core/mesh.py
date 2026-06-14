from loaders.obj_parser import parse_objs, build_interleaved

class Mesh:
    def __init__(self, vertices=None, indices=None, vbo=None, ibo=None, vao=None, shadow_vao=None, path=None):
        self.vertices = vertices
        self.indices = indices

        self.vbo = vbo
        self.ibo = ibo
        self.vao = vao

        self.shadow_vao = shadow_vao

        self.path = path

    def load_model(self, path):
        self.path = path
        vertex_buffer, normal_buffer, tangent_buffer, bitangent_buffer, uv_buffer, index_buffer, normal_index_buffer, uv_index_buffer = parse_objs([path])


        self.vertices, self.indices = build_interleaved(
            vertex_buffer,
            normal_buffer,
            tangent_buffer,
            bitangent_buffer,
            uv_buffer,
            index_buffer,
            normal_index_buffer,
            uv_index_buffer
        )

    def serialize(self):
        return {
            "path": self.path
        }

    @classmethod
    def deserialize(cls, data, ctx):
        mesh = cls()
        mesh.load_model(data["path"])
        return mesh