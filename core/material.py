from loaders.texture_loader import load_texture

class Material:
    def __init__(self, ctx, tex_path, normal_path, heightmap_path, orm_path, height_scale, uv_scale):
        self.ctx = ctx
        self.texture, self.texture_path = load_texture(ctx, tex_path if tex_path else None, "assets/textures/Empty.png")
        self.normal_map, self.normal_map_path = load_texture(ctx, normal_path if normal_path else None, "assets/textures/EmptyNormal.png")
        self.heightmap, self.heightmap_path = load_texture(ctx, heightmap_path if heightmap_path else None, "assets/textures/EmptyHeightmap.png")
        self.orm_map, self.orm_map_path = load_texture(ctx, orm_path if orm_path else None, "assets/textures/EmptyORM.png")
        self.height_scale = height_scale
        self.uv_scale = uv_scale
    
    def load_base_map(self, path):
        self.texture, self.texture_path = load_texture(self.ctx, path if path else None, "assets/textures/Empty.png")
    
    def load_normal_map(self, path):
        self.normal_map, self.normal_map_path = load_texture(self.ctx, path if path else None, "assets/textures/EmptyNormal.png")

    def load_height_map(self, path):
        self.heightmap, self.heightmap_path = load_texture(self.ctx, path if path else None, "assets/textures/EmptyHeightmap.png")

    def load_orm_map(self, path):
        self.orm_map, self.orm_map_path = load_texture(self.ctx, path if path else None, "assets/textures/EmptyORM.png")

    @staticmethod
    def identity(ctx):
        return Material(ctx, None, None, None, None, 0.001, 1)
    
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
    def deserialize(cls, data, ctx):
        return cls(ctx, data["texture_path"], data["normal_map_path"], data["heightmap_path"], data["orm_map_path"], data["height_scale"], data["uv_scale"])