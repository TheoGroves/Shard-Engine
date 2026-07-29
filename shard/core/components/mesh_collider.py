from ..component import component

@component
class MeshCollider:
    __inspect__ = {
    }

    def __init__(self, mesh = None):
        self.entity = None

        self.mesh = mesh