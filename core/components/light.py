from ecs import component
 
@component
class Light:
    def __init__(self, light_type="Directional"):
        self.light_type = light_type
