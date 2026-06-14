from ecs import component
 
@component
class PlayerController:
    def __init__(self, grounded=False):
        self.grounded = grounded
