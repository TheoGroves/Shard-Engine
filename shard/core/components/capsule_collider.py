from ..component import component

@component
class CapsuleCollider:
    __inspect__ = {
        "height": "float",
        "radius": "float",
        "offset": "float"
    }

    def __init__(self, height = 2.0, radius = 1.0, offset = 0.0):
        self.entity = None

        self.height = height
        self.radius = radius
        self.offset = offset

    def serialize(self):
        return {
            "height": self.height,
            "radius": self.radius,
            "offset": self.offset
        }

    @classmethod
    def deserialize(cls, data, engine):
        return cls(data["height"], data["radius"], data["offset"])