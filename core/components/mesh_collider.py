from ecs import component
 
@component
class MeshCollider:
    def __init__(self, mesh, debug):
        self.mesh = mesh
        self.model_path = None
        self.debug = debug