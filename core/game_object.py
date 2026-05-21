from maths.matrices import get_model_matrix
from core.material import Material
from loaders.obj_parser import parse_objs, build_interleaved

class GameObject:
    def __init__(self, name: str, pos, material: Material):
        self.name = name
        self.model = None
        self.set_pos(pos)
        self.material = material

        self.vertices = None
        self.indices = None

        self.vbo = None
        self.ibo = None
        self.vao = None

    def set_pos(self, pos):
        self.model = get_model_matrix((pos[0]*0.1, pos[1]*0.1, pos[2]*0.1))

    def load_model(self, path):
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

