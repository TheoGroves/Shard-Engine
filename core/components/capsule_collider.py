from ..component import component

@component
class CapsuleCollider:
    def __init__(self, height, radius, offset):
        self.height = height
        self.radius = radius
        self.offset = offset