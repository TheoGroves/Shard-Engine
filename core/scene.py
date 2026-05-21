from core.game_object import GameObject

class Scene:
    def __init__(self, name: str):
        self.name = name
        self.game_objects = []

    def add(self, game_object: GameObject):
        self.game_objects.append(game_object)