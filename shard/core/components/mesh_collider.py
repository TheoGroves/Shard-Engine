from ..component import component

@component
class MeshCollider:
    __inspect__ = {
        "path": "mesh"
    }

    def __init__(self, mesh_path="", mesh = None):
        self.entity = None

        self.path = mesh_path
        self.mesh = mesh

    def serialize(self):
        return {
            "path": self.path
        }

    @classmethod
    def deserialize(cls, data, engine):
        return cls(data["path"])