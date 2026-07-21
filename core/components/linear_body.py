from ..component import component
from maths.python import Vec3

@component
class LinearBody:
    def __init__(self):
        self.entity = None

        self.velocity = Vec3(0,0,0)