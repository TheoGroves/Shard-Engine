from ecs import component
 
@component
class Light:
    def __init__(self, light_type="Directional"):
        self.light_type = light_type

    def serialize(self):
        return {
            "light_type": self.light_type
        }
    
    @classmethod
    def deserialize(cls, data, ctx):
        return cls(data["light_type"])