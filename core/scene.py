from rendering.shadow_mapper import ShadowMapper
from collisions.collider import Collider
from ecs import EntityManager
from core.components import Transform, MeshRenderer

class Scene:
    def __init__(self, name: str, renderer, shadow_mapper: ShadowMapper):
        self.name = name
        self.renderer = renderer
        self.shadow_mapper = shadow_mapper
        self.colliders = []
        self.em = EntityManager()

    def add(self, game_object=None):
        eid = self.em.create_entity()
        
        if game_object is None:
            self.em.add_component(eid, Transform.identity())
            return eid
        
        transform = Transform(
            game_object.transform.pos,
            game_object.transform.rot,
            game_object.transform.scale
        )
        self.em.add_component(eid, transform)
        
        if game_object.mesh and len(game_object.mesh.vertices) > 0:
            mesh_renderer = MeshRenderer(game_object.mesh, None, game_object.material)
            mesh_renderer.model_path = game_object.model_path
            self.em.add_component(eid, mesh_renderer)
            
            if self.renderer and self.renderer.program:
                self.renderer.generate_buffers(mesh_renderer)
                if self.shadow_mapper:
                    self.shadow_mapper.generate_shadow_vao(mesh_renderer)
        
        return eid

    def add_collider(self, collider: Collider):
        self.colliders.append(collider)