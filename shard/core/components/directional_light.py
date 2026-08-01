from ..component import component
from shard.maths.python import Vec3

@component
class DirectionalLight:
    __inspect__ = {
        "light_dir": "Vec3"
    }

    def __init__(self, light_dir = Vec3(-0.3, -1.0, -0.2)):
        self.entity = None

        self.light_dir = light_dir

    def serialize(self):
        return {
            "dir_x": self.light_dir.x,
            "dir_y": self.light_dir.y,
            "dir_z": self.light_dir.z
        }

    @classmethod
    def deserialize(cls, data, engine):
        return cls(Vec3(data["dir_x"], data["dir_y"], data["dir_z"]))