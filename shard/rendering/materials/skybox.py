from shard.rendering.texture_slots import *
from shard.rendering.materials.material import Material
from shard.maths.python import Vec3
import time

start_time = time.time()

class SkyboxMaterial(Material):
    def __init__(self, render_engine, asset_manager, hdri: str, exposure=1.0, rotation=0.0, air=1.0, aerosols=1.0, ozone=1.0, cloud_density=0.05, cloud_cover=0.6, sun_colour=Vec3(1.0,1.0,1.0)):
        self.material = render_engine.create_material("assets/shaders/skybox.frag", "assets/shaders/skybox.vert")
        self.proc_material = render_engine.create_material("assets/shaders/proc_skybox.frag", "assets/shaders/skybox.vert")

        self.use_procedural = False

        # HDRI
        self.exposure = exposure
        self.rotation = rotation

        env, _ = asset_manager.get_env_map(hdri)
        self.env = env["environment"]
        self.irr = env["irradiance"]
        render_engine.bind_texture(self.env, ENV_MAP)
        render_engine.update_int(self.material, "uEnvMap", ENV_MAP)

        # Procedural skybox
        self.air = air
        self.aerosols = aerosols
        self.ozone = ozone
        self.sun_colour = sun_colour
        self.cloud_density = cloud_density
        self.cloud_cover = cloud_cover

    def update(self, render_engine, cam, light_dir):
        render_engine.bind_texture(self.env, ENV_MAP)
        render_engine.update_int(self.material, "uEnvMap", ENV_MAP)
        render_engine.update_float(self.material, "uExposure", self.exposure)
        render_engine.update_float(self.material, "uRotation", self.rotation)

        render_engine.update_mat4(self.material, "uView", cam.get_view())
        render_engine.update_mat4(self.material, "uProj", cam.get_projection())

        render_engine.update_float(self.proc_material, "air", self.air)
        render_engine.update_float(self.proc_material, "aerosols", self.aerosols)
        render_engine.update_float(self.proc_material, "ozone", self.ozone)
        render_engine.update_vec3(self.proc_material, "sun_color", self.sun_colour)
        render_engine.update_vec3(self.proc_material, "sun_dir", Vec3(-light_dir.x, -light_dir.y, -light_dir.z))
        render_engine.update_float(self.proc_material, "camHeight", cam.position.y)
        render_engine.update_float(self.proc_material, "time", time.time()-start_time)
        render_engine.update_float(self.proc_material, "cloud_density", self.cloud_density)
        render_engine.update_float(self.proc_material, "cloud_coverage", self.cloud_cover)

        render_engine.update_mat4(self.proc_material, "uView", cam.get_view())
        render_engine.update_mat4(self.proc_material, "uProj", cam.get_projection())

    def draw_inspector(self, inspector):
        inspector.edit_bool(f"use_procedural##{id(self)}", self)
        if self.use_procedural:
            inspector.edit_float(f"air##{id(self)}", self)
            inspector.edit_float(f"aerosols##{id(self)}", self)
            inspector.edit_float(f"ozone##{id(self)}", self)
            inspector.edit_float(f"cloud_density##{id(self)}", self)
            inspector.edit_float(f"cloud_cover##{id(self)}", self)
        else:
            inspector.edit_texture_env("env", self)
            inspector.edit_float(f"exposure##{id(self)}", self)
            inspector.edit_float(f"rotation##{id(self)}", self)

    def serialize(self):
        return f"Skybox#{self.env}#{self.exposure}#{self.rotation}"

    @staticmethod
    def deserialize(engine, asset_manager, logger, data):
        _, env, exposure, rotation = data["material"].split("#")

        return SkyboxMaterial(engine, asset_manager, asset_manager.env_paths[int(env)], float(exposure), float(rotation))