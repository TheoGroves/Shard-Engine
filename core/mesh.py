import numpy as np
import pickle
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

    @classmethod
    def deserialize(cls, data, ctx, asset_manager):
        mesh = asset_manager.get_mesh(data)
        return mesh
    
    def save_cooked(self, path):
        data = {
            "vertices": self.vertices.tobytes(),
            "indices": self.indices.tobytes(),
            "path": str(self.path)
        }

        with open(path, "wb") as f:
            pickle.dump(data, f)

    def load_cooked(self, path):
        with open(path, "rb") as f:
            data = pickle.load(f)

        self.vertices = np.frombuffer(data["vertices"], dtype="f4")
        self.indices = np.frombuffer(data["indices"], dtype="i4")
        self.path = data["path"]