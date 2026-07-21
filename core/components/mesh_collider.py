from ..component import component

@component
class MeshCollider:
    def __init__(self, mesh):
        self.entity = None

        self.mesh = mesh