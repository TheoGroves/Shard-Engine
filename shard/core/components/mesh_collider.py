from ..component import component

@component
class MeshCollider:
    __inspect__ = {
    }

    def __init__(self, mesh = None):
        self.entity = None

        self.mesh = mesh

    def serialize(self):
        return {}

    @classmethod
    def deserialize(cls, data, engine):
        return cls()