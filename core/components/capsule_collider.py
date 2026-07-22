from ..component import component

@component
class CapsuleCollider:
    __inspect__ = [
        "height",
        "radius",
        "offset"
    ]

    def __init__(self, height, radius, offset):
        self.entity = None

        self.height = height
        self.radius = radius
        self.offset = offset