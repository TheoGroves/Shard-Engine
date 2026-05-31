from core.game_object import GameObject
from rendering.shadow_mapper import ShadowMapper
from collisions.collider import Collider
from collisions.spatial_grid import SpatialGrid

class Scene:
    def __init__(self, name: str, renderer, shadow_mapper: ShadowMapper):
        self.name = name
        self.renderer = renderer
        self.shadow_mapper = shadow_mapper
        self.game_objects = []
        self.colliders = []

    def add(self, game_object: GameObject):
        self.renderer.generate_buffers(game_object)
        self.shadow_mapper.generate_shadow_vao(game_object)
        self.game_objects.append(game_object)

    def add_collider(self, collider: Collider):
        self.colliders.append(collider)

    def get_collision_triangles(self, grid: SpatialGrid):
        triangles = []

        for collider in self.colliders:
            for tri in collider.get_world_triangles():
                idx = len(triangles)

                triangles.append(tri)

                a,b,c = tri

                grid.insert_triangle(
                    idx,
                    a,b,c
                )
            
        return triangles