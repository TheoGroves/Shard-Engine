from rendering import RenderEngine
from core.logger import *

class TestUI:
    def __init__(self, render_engine: RenderEngine):
        log_info("Created Test UI.")
        self.render_engine = render_engine

    def update(self):
        if self.render_engine.begin_window("Test Window"):
            self.render_engine.text("Hello World")
        self.render_engine.end_window()