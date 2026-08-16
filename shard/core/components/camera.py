from ..component import component

@component
class Camera:
    __inspect__ = {
        "active": "bool",
        "near_plane": "float",
        "far_plane": "float"
    }
    def __init__(self, active: bool = False, near_plane: float = 0.1, far_plane: float = 100.0):
        self.entity = None

        self.active = active
        self.near_plane = near_plane
        self.far_plane = far_plane

    def serialize(self):
        return {
            "active": self.active
        }

    @classmethod
    def deserialize(cls, data, engine):
        return cls(data["active"])