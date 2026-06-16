from ecs import component
from core.mesh import Mesh

@component
class MeshCollider:
    def __init__(self, mesh, debug):
        self.mesh = mesh
        self.debug = debug

    def serialize(self):
        return {
            "path": self.mesh.path if self.mesh else None,
            "debug": self.debug
        }
    
    @classmethod
    def deserialize(cls, data, ctx, asset_manager):
        mesh = Mesh.deserialize(data["path"], ctx, asset_manager)
        debug = data["debug"]

        return cls(mesh, debug)