from shard.rendering.texture_slots import *
from shard.rendering.materials.material import Material

class PBRMaterial(Material):
    def __init__(self, render_engine, asset_manager, logger, albedo: str, normal: str, height: str, orm: str, uv_scale=1.0):
        self.material = render_engine.create_material("assets/shaders/standard.frag", "assets/shaders/standard.vert")

        self.albedo, _ = asset_manager.get_texture(albedo, "assets/textures/Empty.png", logger)
        render_engine.bind_texture(self.albedo, ALBEDO)
        render_engine.update_int(self.material, "uAlbedo", ALBEDO)

        self.normal, _ = asset_manager.get_texture(normal, "assets/textures/EmptyNormal.png", logger)
        render_engine.bind_texture(self.normal, NORMAL)
        render_engine.update_int(self.material, "uNormal", NORMAL)

        self.height, _ = asset_manager.get_texture(height, "assets/textures/EmptyHeightmap.png", logger)
        render_engine.bind_texture(self.height, HEIGHT_MAP)
        render_engine.update_int(self.material, "uHeightMap", HEIGHT_MAP)
        render_engine.update_float(self.material, "uHeightScale", 0.0)

        self.orm, _ = asset_manager.get_texture(orm, "assets/textures/EmptyORM.png", logger)
        render_engine.bind_texture(self.orm, ORM)
        render_engine.update_int(self.material, "uOrmMap", ORM)

        self.uv_scale = uv_scale
        render_engine.update_float(self.material, "uUVScale", self.uv_scale)

    def update(self, render_engine, cam, light_dir, env, irr):
        render_engine.bind_texture(self.albedo, ALBEDO)
        render_engine.update_int(self.material, "uAlbedo", ALBEDO)

        render_engine.bind_texture(self.normal, NORMAL)
        render_engine.update_int(self.material, "uNormal", NORMAL)

        render_engine.bind_texture(self.height, HEIGHT_MAP)
        render_engine.update_int(self.material, "uHeightMap", HEIGHT_MAP)

        render_engine.bind_texture(self.orm, ORM)
        render_engine.update_int(self.material, "uOrmMap", ORM)

        if env is not None:
            render_engine.bind_texture(env, ENV_MAP)
            render_engine.update_int(self.material, "uEnvMap", ENV_MAP)

        if irr is not None:
            render_engine.bind_texture(irr, IRR_MAP)
            render_engine.update_int(self.material, "uIrrMap", IRR_MAP)

        render_engine.bind_texture(render_engine.get_shadow_depth(), SHADOW_MAP)
        render_engine.update_int(self.material, "uShadowMap", SHADOW_MAP)

        render_engine.update_mat4(self.material, "uView", cam.get_view())
        render_engine.update_mat4(self.material, "uProj", cam.get_projection())

        render_engine.update_mat4(self.material, "uLightSpace", render_engine.get_light_space())

        render_engine.update_vec3(self.material, "uCamPos", cam.position)

        render_engine.update_vec3(self.material, "uLightDir", light_dir)
        render_engine.update_float(self.material, "uTonemapExposure", 3.0)

        render_engine.update_float(self.material, "uUVScale", self.uv_scale)

    def draw_inspector(self, inspector):
        inspector.edit_texture(f"albedo", self)
        inspector.edit_texture(f"normal", self)
        inspector.edit_texture(f"height", self)
        inspector.edit_texture(f"orm", self)
        inspector.edit_float(f"uv_scale##{id(self)}", self)

    def serialize(self):
        return f"PBR#{self.albedo}#{self.normal}#{self.height}#{self.orm}#{self.uv_scale}"

    @staticmethod
    def deserialize(engine, asset_manager, logger, data):
        _, albedo, normal, height, orm, uv_scale = data["material"].split("#")

        return PBRMaterial(engine, asset_manager, logger, asset_manager.texture_paths[int(albedo)], asset_manager.texture_paths[int(normal)], asset_manager.texture_paths[int(height)], asset_manager.texture_paths[int(orm)], float(uv_scale))