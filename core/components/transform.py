import numpy as np
from ecs import component
from maths.matrices import get_model_matrix

@component
class Transform:
    def __init__(self, pos=np.array([0, 0, 0], dtype=np.float32), rot=np.array([0, 0, 0], dtype=np.float32), scale=np.array([1, 1, 1], dtype=np.float32)):
        self.pos = pos
        self.rot = rot
        self.scale = scale
        self.front = np.array([0, 0, -1], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.array([1, 0, 0], dtype=np.float32)
        self.model = get_model_matrix(self.pos, self.rot, self.scale)

        self.world_up = np.array([0, 1, 0], dtype=np.float32)

    @staticmethod
    def identity():
        return Transform()
    
    @staticmethod
    def _encode_array(v):
        if isinstance(v, tuple):
            return v
        try:
            return {"__type__": "ndarray", "__value__": v.tolist()}
        except AttributeError:
            return v
    
    @staticmethod
    def _decode_array(v):
        if isinstance(v, dict) and v.get("__type__") == "ndarray":
            return np.array(v["__value__"])
        return v

    def serialize(self):
        return {k: self._encode_array(getattr(self, k)) for k in ("pos", "rot", "scale")}
    
    @classmethod
    def deserialize(cls, data, ctx):
        pos = cls._decode_array(data["pos"])
        rot = cls._decode_array(data["rot"])
        scale = cls._decode_array(data["scale"])
        return cls(pos, rot, scale)