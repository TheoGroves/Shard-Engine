from shard.rendering.texture_slots import *
from shard.rendering.materials.material import Material

class SkyboxMaterial(Material):
    def __init__(self, engine, asset_manager, hdri: str, exposure=1.0, rotation=0.0):
        self.material = engine.create_material("assets/shaders/skybox.frag", "assets/shaders/skybox.vert")

        self.exposure = exposure
        self.rotation = rotation

        env, _ = asset_manager.get_env_map(hdri)
        self.env = env["environment"]
        self.irr = env["irradiance"]
        engine.bind_texture(self.env, ENV_MAP)
        engine.update_int(self.material, "uEnvMap", ENV_MAP)

    def update(self, engine, cam):
        engine.bind_texture(self.env, ENV_MAP)
        engine.update_int(self.material, "uEnvMap", ENV_MAP)
        engine.update_float(self.material, "uExposure", self.exposure)
        engine.update_float(self.material, "uRotation", self.rotation)

        engine.update_mat4(self.material, "uView", cam.get_view())
        engine.update_mat4(self.material, "uProj", cam.get_projection())

    def draw_inspector(self, inspector):
        inspector.edit_texture_env("env", self)
        inspector.edit_float(f"exposure##{id(self)}", self)
        inspector.edit_float(f"rotation##{id(self)}", self)


    def serialize(self):
        return f"Skybox#{self.env}#{self.exposure}#{self.rotation}"

    @staticmethod
    def deserialize(engine, asset_manager, logger, data):
        _, env, exposure, rotation = data["material"].split("#")

        return SkyboxMaterial(engine, asset_manager, asset_manager.env_paths[int(env)], float(exposure), float(rotation))