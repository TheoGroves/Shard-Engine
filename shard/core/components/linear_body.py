from ..component import component
from shard.maths.python import Vec3

@component
class LinearBody:
    __inspect__ = {
        "velocity": "Vec3"
    }

    def __init__(self, velocity = Vec3(0,0,0)):
        self.entity = None

        self.velocity = velocity

    def serialize(self):
        return {
            "velocity_x": self.velocity.x,
            "velocity_y": self.velocity.y,
            "velocity_z": self.velocity.z
        }

    @classmethod
    def deserialize(cls, data, engine):
        return cls(Vec3(data["velocity_x"], data["velocity_y"], data["velocity_z"]))