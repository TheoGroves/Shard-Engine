import time

from rendering.shadow_mapper import ShadowMapper
from ecs import EntityManager, Serializer, Deserializer
from core.components import Transform, MeshRenderer

class Scene:
    def __init__(self, name: str, renderer, shadow_mapper: ShadowMapper, asset_manager):
        self.name = name
        self.renderer = renderer
        self.shadow_mapper = shadow_mapper
        self.em = EntityManager()
        self.asset_manager = asset_manager

        self._serializer = Serializer()
        self._deserializer = Deserializer()

    def add(self, game_object=None):
        eid, _ = self.em.create_entity()
        
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
            mesh_renderer.mesh.mesh = game_object.mesh.path
            self.em.add_component(eid, mesh_renderer)
            
            if self.renderer and self.renderer.program:
                self.renderer.generate_buffers(mesh_renderer)
                if self.shadow_mapper:
                    self.shadow_mapper.generate_shadow_vao(mesh_renderer)
        
        return eid
    
    def generate_buffers(self):
        for eid in self.em.query("MeshRenderer"):
            mr = self.em.entities[eid].components["MeshRenderer"]
            self.renderer.generate_buffers(mr)
            self.shadow_mapper.generate_shadow_vao(mr)        
    
    def save_scene(self, scene_name):
        self._serializer.save_scene(self.em, f"scenes/{scene_name}.json")

    def load_scene(self, scene_name, ctx):
        self.em.clear()
        self._deserializer.load_scene(self.em, f"scenes/{scene_name}.json", ctx, self.asset_manager)