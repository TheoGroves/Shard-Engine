from ..component import component

@component
class MeshRenderer:
    def __init__(self):
        self.mesh_handle = None
        self.material = None