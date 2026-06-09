from ecs import component
 
@component
class MeshRenderer:
    def __init__(self, mesh, model_path, material):
        self.mesh = mesh
        self.model_path = model_path
        self.material = material