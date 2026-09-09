from shard.rendering import RenderEngine
from shard.core.entity import EntityManager, Serializer, Deserializer
from shard.tools import PrimitiveGenerator
import time

class MainMenu:
    def __init__(self, render_engine: RenderEngine, entity_manager: EntityManager, primitive_generator: PrimitiveGenerator):
        self.render_engine = render_engine
        self.entity_manager = entity_manager
        self.primitive_generator = primitive_generator

    def update(self, engine, serializer: Serializer, deserializer: Deserializer, logger):
        if self.render_engine.begin_menu_bar():
            if self.render_engine.begin_menu("File"):
                if self.render_engine.button("Save Scene", 0, 0):
                    serializer.save_scene(self.entity_manager, "scenes/main.json", logger)

                if self.render_engine.button("Load Scene", 0, 0):
                    deserializer.load_scene(self.entity_manager, engine, "scenes/main.json", logger)

                self.render_engine.separator()

                if self.render_engine.button("Restore Previous Save", 0, 0):
                    deserializer.restore_backup(self.entity_manager, engine, "scenes/main.json", logger)
                    logger.log_info("Save restored.")

                self.render_engine.end_menu()

            if self.render_engine.begin_menu("Tools"):
                if self.render_engine.button("Generate Primitives", 0, 0):
                    start = time.perf_counter()
                    self.primitive_generator.generate_quad(1)
                    self.primitive_generator.generate_cube(1)
                    self.primitive_generator.generate_sphere(0.5, 3)
                    self.primitive_generator.generate_cylinder(0.5, 2, 3)
                    logger.log_info(f"Generated primitives in {(time.perf_counter()-start)*1000:.1f}ms")

                self.render_engine.end_menu()

            self.render_engine.end_menu_bar()
