from ecs import component
 
@component
class CapsuleCollider:
    def __init__(self, radius=0.3, height=1.8, offset=0):
        self.radius = radius
        self.height = height
        self.offset = offset