from ecs import component
 
@component
class PlayerController:
    def __init__(self):
        self.grounded = False
