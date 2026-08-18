from ..component import component
from shard.maths.python import Vec3, model_matrix, radians
@component
class Transform:
    __inspect__ = {
        "pos": "Vec3",
        "rot": "Vec3",
        "scale": "Vec3"
    }

    def __init__(self, pos: Vec3 = Vec3(0,0,0), rot: Vec3 = Vec3(0,0,0), scale: Vec3 = Vec3(1,1,1)):
        self.entity = None
        
        self.pos = pos
        self.rot = rot
        self.scale = scale

        self.last_pos = pos
        self.displacement = Vec3(0,0,0)
        self.velocity = Vec3(0,0,0) # Derived velocity, position is authoritative

        self.world_pos = pos

        self.forward = Vec3(0,0,1)
        self.right = Vec3(1,0,0)
        self.up = Vec3(0,1,0)

        self.world_forward = Vec3(0,0,1)
        self.world_right = Vec3(1,0,0)
        self.world_up = Vec3(0,1,0)

        self.model = model_matrix(pos, rot, scale)
        self.world = model_matrix(pos, rot, scale)

        self.parent = None
        self.children = []

    def serialize(self):
        return {
            "pos_x": self.pos.x,
            "pos_y": self.pos.y,
            "pos_z": self.pos.z,

            "rot_x": self.rot.x,
            "rot_y": self.rot.y,
            "rot_z": self.rot.z,

            "scale_x": self.scale.x,
            "scale_y": self.scale.y,
            "scale_z": self.scale.z,

            "parent": self.parent,
            "children": "#".join(list(map(str,self.children)))
        }

    @classmethod
    def deserialize(cls, data, engine):
        t = cls(Vec3(data["pos_x"], data["pos_y"], data["pos_z"]), Vec3(data["rot_x"], data["rot_y"], data["rot_z"]), Vec3(data["scale_x"], data["scale_y"], data["scale_z"]))
        t.parent = int(data["parent"]) if data["parent"] is not None else None
        children = data["children"]
        t.children = ([int(x) for x in children.split("#") if x] if children not in (None, "") else [])

        return t