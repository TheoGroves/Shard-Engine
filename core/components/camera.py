from ecs import component

@component
class Camera:
    def __init__(self, width, height, active=True):
        self.active = active
        self.width = width
        self.height = height
        self.fov = 90.0
        self.near = 0.1
        self.far = 1000.0
        self.aspect = width / height
        self.exposure = 2

    def serialize(self):
        return {
            "width": self.width,
            "height": self.height,
            "active": self.active
        }
    
    @classmethod
    def deserialize(cls, data, ctx):
        return cls(data["width"], data["height"], data["active"])