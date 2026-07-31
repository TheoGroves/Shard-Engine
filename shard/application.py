import traceback
import time


class Application:
    def __init__(self):
        from .bootstrap import bootstrap
        from factories.default import build_scene

        self.engine = bootstrap()
        self.scene = build_scene(self.engine)

    def run(self):
        dt = 1/60

        try:
            while not self.engine.render_engine.should_close():
                s = time.perf_counter()
                self.update(dt)
                dt = time.perf_counter() - s

        finally:
            self.engine.render_engine.shutdown()
            self.engine.console.cleanup()

    def update(self, dt):
        player_input = self.engine.render_engine.get_input()

        self.safe_update("FlyController", self.engine.fly_controller_system.update, player_input, dt)
        self.safe_update("Physics", self.engine.physics_system.update, -9.81, dt)
        self.safe_update("Collision", self.engine.collision_system.update)
        self.safe_update("Transform", self.engine.transform_system.update)
        self.safe_update("Camera", self.engine.camera_system.update, self.engine.logger)
        self.safe_update("MeshRenderer", self.engine.mesh_renderer_system.update, self.engine.render_engine, self.scene.light_dir, self.engine.camera_system.render_camera, self.engine.viewport)

        self.safe_update("MainMenuUI", self.engine.main_menu.update, self.engine, self.engine.serializer, self.engine.deserializer, self.engine.logger)
        self.safe_update("ConsoleUI", self.engine.console.update, self.engine.logger)
        self.safe_update("ViewportUI", self.engine.viewport_ui.update, self.engine.viewport, self.engine.camera_system.render_camera)
        self.safe_update("HierarchyUI", self.engine.hierarchy.update)
        self.safe_update("InspectorUI", self.engine.inspector.update, self.engine.logger)
        self.safe_update("ProfilerUI", self.engine.profiler.update, dt)

        self.engine.render_engine.end_frame()

    def safe_update(self, name, callback, *args):
        try:
            callback(*args)
        except Exception as e:
            self.engine.logger.log_fatal(f"Unhandled exception in system {name}:\n{traceback.format_exc()}")
