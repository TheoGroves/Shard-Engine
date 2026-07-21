from rendering import RenderEngine
from core.logger import *

class ViewportUI:
    def __init__(self, render_engine: RenderEngine):
        self.render_engine = render_engine

    def update(self, viewport, camera):
        if self.render_engine.begin_window("Viewport"):
            available_region = self.render_engine.get_available_region()

            width = max(1,int(abs(available_region.x)))
            height = max(1,int(abs(available_region.y)))

            camera.aspect = width/height

            viewport.resize(width, height)

            self.render_engine.image(viewport.colour, viewport.width, viewport.height)

        self.render_engine.end_window()

