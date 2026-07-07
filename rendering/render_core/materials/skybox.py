from rendering.render_core.texture_slots import *

class SkyboxMaterial:
    def __init__(self, engine, asset_manager, hdri: str):
        self.material = engine.create_material("assets/shaders/skybox.frag", "assets/shaders/skybox.vert")

        self.env, _ = asset_manager.get_env_map(hdri)
        engine.bind_texture(self.env, ENV_MAP)
        engine.update_int(self.material, "uEnvMap", ENV_MAP)

    def update(self, engine, cam):
        engine.update_mat4(self.material, "uView", cam.get_view())
        engine.update_mat4(self.material, "uProj", cam.get_projection())