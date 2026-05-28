from core.game_object import GameObject
from rendering.shadow_mapper import ShadowMapper

class Scene:
    def __init__(self, name: str, renderer, shadow_mapper: ShadowMapper):
        self.name = name
        self.renderer = renderer
        self.shadow_mapper = shadow_mapper
        self.game_objects = []

    def add(self, game_object: GameObject):
        self.renderer.generate_buffers(game_object)
        self.shadow_mapper.generate_shadow_vao(game_object)
        self.game_objects.append(game_object)