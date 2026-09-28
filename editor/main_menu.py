from shard.rendering import RenderEngine, Theme
from shard.core.entity import EntityManager, Serializer, Deserializer
from shard.tools import PrimitiveGenerator
import time

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

                self.render_engine.separator()

                if self.render_engine.button("Restore Previous Save", 0, 0):
                    deserializer.restore_backup(self.entity_manager, engine, "scenes/main.json", logger)
                    logger.log_info("Save restored.")

                self.render_engine.end_menu()

            if self.render_engine.begin_menu("Tools"):
                if self.render_engine.button("Generate Primitives", 0, 0):
                    start = time.perf_counter()
                    engine.generate_primitives()
                    logger.log_info(f"Generated primitives in {(time.perf_counter()-start)*1000:.1f}ms")

                self.render_engine.end_menu()

            if self.render_engine.begin_menu("View"):
                if self.render_engine.button("Themes", 0, 0):
                    self.render_engine.open_popup("edit_themes")
                self.render_engine.end_menu()

            self.render_engine.end_menu_bar()

        if self.render_engine.begin_popup("edit_themes"):
            current_theme = self.render_engine.get_theme().name

            for theme in Theme.__members__.keys():
                # Align themes and add a tick by currently selected theme
                button_text = f"  {theme}"
                if theme == current_theme:
                    button_text = f"✓ {theme}"

                if self.render_engine.button(button_text, 0, 0):
                    new_theme = Theme[theme]

                    self.render_engine.set_theme(new_theme)

            self.render_engine.end_popup()
