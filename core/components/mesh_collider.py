from ecs import component
from core.mesh import Mesh

@component
class MeshCollider:
    def __init__(self, mesh, debug):
        self.mesh = mesh
        self.debug = debug

    def serialize(self):
        return {
            "mesh": self.mesh.serialize() if self.mesh else None,
            "debug": self.debug
        }
    
    @classmethod
    def deserialize(cls, data, ctx):
        mesh = Mesh.deserialize(data["mesh"], ctx)
        debug = data["debug"]

        return cls(mesh, debug)