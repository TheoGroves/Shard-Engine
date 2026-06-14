from ecs import component
from core.material import Material
from core.mesh import Mesh

@component
class MeshRenderer:
    def __init__(self, mesh, path, material):
        self.mesh = mesh
        self.material = material

    def serialize(self):
        return {
            "mesh": self.mesh.serialize() if self.mesh else None,
            "material": self.material.serialize() if self.material else None
        }
    
    @classmethod
    def deserialize(cls, data, ctx):
        mesh = Mesh.deserialize(data["mesh"], ctx)

        material = None
        if data["material"]:
            material = Material.deserialize(data["material"], ctx)

        return cls(mesh, None, material)