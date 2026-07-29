from ..component import component
from shard.maths.python import Vec3

@component
class LinearBody:
    __inspect__ = [
        "velocity"
    ]

    def __init__(self):
        self.entity = None

        self.velocity = Vec3(0,0,0)