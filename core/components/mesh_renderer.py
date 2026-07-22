from ..component import component

@component
class MeshRenderer:
    __inspect__ = [
        "mesh_handle"
    ]

    def __init__(self):
        self.entity = None

        self.mesh_handle = None
        self.material = None