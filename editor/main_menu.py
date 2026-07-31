from shard.rendering import RenderEngine
from shard.core.entity import EntityManager, Serializer, Deserializer

class MainMenu:
    def __init__(self, render_engine: RenderEngine, entity_manager: EntityManager):
        self.render_engine = render_engine
        self.entity_manager = entity_manager

    def update(self, engine, serializer: Serializer, deserializer: Deserializer, logger):
        if self.render_engine.begin_menu_bar():
            if self.render_engine.begin_menu("File"):
                if self.render_engine.button("Save Scene", 0, 0):
                    serializer.save_scene(self.entity_manager, "scenes/main.json", logger)

                if self.render_engine.button("Load Scene", 0, 0):
                    deserializer.load_scene(self.entity_manager, engine, "scenes/main.json", logger)

                self.render_engine.end_menu()

            self.render_engine.end_menu_bar()
