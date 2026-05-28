from maths.matrices import get_model_matrix
from core.material import Material
from core.transform import Transform
from loaders.obj_parser import parse_objs, build_interleaved

class GameObject:
    def __init__(self, name: str, transform: Transform, material: Material):
        self.name = name
        self.model = None
        self.set_transform(transform)
        self.material = material

        self.vertices = None
        self.indices = None

        self.vbo = None
        self.ibo = None
        self.vao = None

    def set_transform(self, transform: Transform):
        self.model = get_model_matrix((transform.pos[0], transform.pos[1], transform.pos[2]), transform.rot, transform.scale)

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

