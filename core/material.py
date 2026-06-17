
class Material:
    def __init__(self, ctx, asset_manager, tex_path="assets/textures/Empty.png", normal_path="assets/textures/EmptyNormal.png", heightmap_path="assets/textures/EmptyHeightmap.png", orm_path="assets/textures/EmptyORM.png", height_scale=0.01, uv_scale=1):
        self.ctx = ctx
        self.asset_manager = asset_manager
        self.texture, self.texture_path = self.asset_manager.get_texture(tex_path if tex_path else None, "assets/textures/Empty.png")
        self.normal_map, self.normal_map_path =  self.asset_manager.get_texture(normal_path if normal_path else None, "assets/textures/EmptyNormal.png")
        self.heightmap, self.heightmap_path =  self.asset_manager.get_texture(heightmap_path if heightmap_path else None, "assets/textures/EmptyHeightmap.png")
        self.orm_map, self.orm_map_path =  self.asset_manager.get_texture(orm_path if orm_path else None, "assets/textures/EmptyORM.png")
        self.height_scale = height_scale
        self.uv_scale = uv_scale
    
    def load_base_map(self, path):
        self.texture, self.texture_path =  self.asset_manager.get_texture(path if path else None, "assets/textures/Empty.png")
    
    def load_normal_map(self, path):
        self.normal_map, self.normal_map_path =  self.asset_manager.get_texture(path if path else None, "assets/textures/EmptyNormal.png")

    def load_height_map(self, path):
        self.heightmap, self.heightmap_path =  self.asset_manager.get_texture(path if path else None, "assets/textures/EmptyHeightmap.png")

    def load_orm_map(self, path):
        self.orm_map, self.orm_map_path =  self.asset_manager.get_texture(path if path else None, "assets/textures/EmptyORM.png")

    @staticmethod
    def identity(ctx, asset_manager):
        return Material(ctx, asset_manager, None, None, None, None, 0.001, 1)
    
    def serialize(self):
        return {
            "texture_path": self.texture_path,
            "normal_map_path": self.normal_map_path,
            "heightmap_path": self.heightmap_path,
            "orm_map_path": self.orm_map_path,
            "height_scale": self.height_scale,
            "uv_scale": self.uv_scale
        }

    @classmethod
    def deserialize(cls, data, ctx, asset_manager):
        return cls(ctx, asset_manager, data["texture_path"], data["normal_map_path"], data["heightmap_path"], data["orm_map_path"], data["height_scale"], data["uv_scale"])