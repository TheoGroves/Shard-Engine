from shard.rendering.texture_slots import *
from shard.rendering.materials.material import Material

class PBRMaterial(Material):
    def __init__(self, engine, asset_manager, logger, albedo: str, normal: str, height: str, orm: str):
        self.material = engine.create_material("assets/shaders/standard.frag", "assets/shaders/standard.vert")

        self.albedo, _ = asset_manager.get_texture(albedo, "assets/textures/Empty.png", logger)
        engine.bind_texture(self.albedo, ALBEDO)
        engine.update_int(self.material, "uAlbedo", ALBEDO)

        self.normal, _ = asset_manager.get_texture(normal, "assets/textures/EmptyNormal.png", logger)
        engine.bind_texture(self.normal, NORMAL)
        engine.update_int(self.material, "uNormal", NORMAL)

        self.height, _ = asset_manager.get_texture(height, "assets/textures/EmptyHeightmap.png", logger)
        engine.bind_texture(self.height, HEIGHT_MAP)
        engine.update_int(self.material, "uHeightMap", HEIGHT_MAP)
        engine.update_float(self.material, "uHeightScale", 0.01)

        self.orm, _ = asset_manager.get_texture(orm, "assets/textures/EmptyORM.png", logger)
        engine.bind_texture(self.orm, ORM)
        engine.update_int(self.material, "uOrmMap", ORM)

        self.uv_scale = 1.0
        engine.update_float(self.material, "uUVScale", self.uv_scale)

    def update(self, engine, cam, light_dir, env, irr):
        engine.bind_texture(self.albedo, ALBEDO)
        engine.update_int(self.material, "uAlbedo", ALBEDO)

        engine.bind_texture(self.normal, NORMAL)
        engine.update_int(self.material, "uNormal", NORMAL)

        engine.bind_texture(self.height, HEIGHT_MAP)
        engine.update_int(self.material, "uHeightMap", HEIGHT_MAP)

        engine.bind_texture(self.orm, ORM)
        engine.update_int(self.material, "uOrmMap", ORM)

        if env is not None:
            engine.bind_texture(env, ENV_MAP)
            engine.update_int(self.material, "uEnvMap", ENV_MAP)

        if irr is not None:
            engine.bind_texture(irr, IRR_MAP)
            engine.update_int(self.material, "uIrrMap", IRR_MAP)

        engine.bind_texture(engine.get_shadow_depth(), SHADOW_MAP)
        engine.update_int(self.material, "uShadowMap", SHADOW_MAP)

        engine.update_mat4(self.material, "uView", cam.get_view())
        engine.update_mat4(self.material, "uProj", cam.get_projection())

        engine.update_mat4(self.material, "uLightSpace", engine.get_light_space())

        engine.update_vec3(self.material, "uCamPos", cam.position)

        engine.update_vec3(self.material, "uLightDir", light_dir)
        engine.update_float(self.material, "uTonemapExposure", 3.0)

        engine.update_float(self.material, "uUVScale", self.uv_scale)

    def draw_inspector(self, inspector):
        inspector.edit_texture(f"albedo", self)
        inspector.edit_texture(f"normal", self)
        inspector.edit_texture(f"height", self)
        inspector.edit_texture(f"orm", self)
        inspector.edit_float(f"uv_scale##{id(self)}", self)