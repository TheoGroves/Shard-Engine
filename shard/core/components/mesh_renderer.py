from ..component import component

@component
class MeshRenderer:
    __inspect__ = {
        "mesh_handle": "mesh",
        "material": "material"
    }

    def __init__(self):
        self.entity = None

        self.mesh_handle = 1
        self.material = None