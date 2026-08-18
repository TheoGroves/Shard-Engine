import traceback
import time


class Application:
    def __init__(self):
        from .bootstrap import bootstrap
        from factories.default import build_scene
        from shard.loaders import load_icon

        self.engine = bootstrap()
        self.scene = build_scene(self.engine)
        load_icon(self.engine.render_engine, "shard/icon.png")

    def run(self):
        dt = 1/60
        self.engine.audio_engine.initialize()

        try:
            self.engine.systems.scripting.start()
            while not self.engine.render_engine.should_close():
                s = time.perf_counter()
                self.update(dt)
                dt = time.perf_counter() - s

        finally:
            self.engine.audio_engine.shutdown()
            self.engine.render_engine.shutdown()
            self.engine.ui.console.cleanup()

    def update(self, dt):
        player_input = self.engine.render_engine.get_input()

        self.engine.systems.scripting.update()

        self.safe_update("FlyController", self.engine.systems.fly_controller.update, player_input, dt)
        self.safe_update("Physics", self.engine.systems.physics.update, -9.81, dt)
        self.safe_update("Collision", self.engine.systems.collision.update, self.engine)
        self.safe_update("Transform", self.engine.systems.transform.update, dt)
        self.safe_update("Camera", self.engine.systems.camera.update, self.engine.logger, self.engine.audio_engine)
        self.safe_update("MeshRenderer", self.engine.systems.mesh_renderer.update, self.engine.render_engine, self.engine.systems.camera.render_camera, self.engine.viewport)

        self.safe_update("MainMenuUI", self.engine.ui.main_menu.update, self.engine, self.engine.serializer, self.engine.deserializer, self.engine.logger)
        self.safe_update("ConsoleUI", self.engine.ui.console.update, self.engine.logger)
        self.safe_update("ViewportUI", self.engine.ui.viewport.update, self.engine.viewport, self.engine.systems.camera.render_camera)
        self.safe_update("HierarchyUI", self.engine.ui.hierarchy.update)
        self.safe_update("InspectorUI", self.engine.ui.inspector.update, self.engine.logger)
        self.safe_update("ProfilerUI", self.engine.ui.profiler.update, dt)

        self.engine.render_engine.end_frame()

        self.engine.audio_engine.cleanup()

        self.engine.dt = dt

    def safe_update(self, name, callback, *args):
        try:
            callback(*args)
        except Exception as e:
            self.engine.logger.log_fatal(f"Unhandled exception in system {name}:\n{traceback.format_exc()}")
