from core.game_object import GameObject
from rendering.shadow_mapper import ShadowMapper

class Scene:
    def __init__(self, name: str, shadow_mapper: ShadowMapper):
        self.name = name
        self.shadow_mapper = shadow_mapper
        self.game_objects = []

    def add(self, game_object: GameObject):
        self.shadow_mapper.generate_shadow_vao(game_object)
        self.game_objects.append(game_object)