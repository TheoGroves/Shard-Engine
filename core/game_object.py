from maths.matrices import get_model_matrix, decompose_model_matrix
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

        self.model_path = None

    def set_transform(self, transform: Transform):
        self.model = get_model_matrix(transform.pos, transform.rot, transform.scale)

    def get_transform(self):
        pos, rot, scale = decompose_model_matrix(self.model)
        return Transform(pos, rot, scale)

    def load_model(self, path):
        self.model_path = path
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

