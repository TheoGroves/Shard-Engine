from PIL import Image
import moderngl

class Material:
    def __init__(self, ctx, tex_path, normal_path, heightmap_path, orm_path, height_scale, uv_scale):
        self.ctx = ctx
        self.texture = self.load_texture(f"assets/textures/{tex_path}" if tex_path else None, "assets/textures/Empty.png")
        self.normal_map = self.load_texture(f"assets/textures/{normal_path}" if normal_path else None, "assets/textures/EmptyNormal.png")
        self.heightmap = self.load_texture(f"assets/textures/{heightmap_path}" if heightmap_path else None, "assets/textures/EmptyHeightmap.png")
        self.orm_map = self.load_texture(f"assets/textures/{orm_path}" if orm_path else None, "assets/textures/EmptyORM.png")
        self.height_scale = height_scale
        self.uv_scale = uv_scale

    def load_texture(self, path, fallback):
        img = Image.open(path if path else fallback).convert("RGBA")
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        tex = self.ctx.texture(img.size, 4, img.tobytes())
        tex.build_mipmaps()
        tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)

        return tex
    
    def load_base_map(self, path):
        self.texture = self.load_texture(path if path else None, "assets/textures/Empty.png")
    
    def load_normal_map(self, path):
        self.normal_map = self.load_texture(path if path else None, "assets/textures/EmptyNormal.png")

    def load_height_map(self, path):
        self.heightmap = self.load_texture(path if path else None, "assets/textures/EmptyHeightmap.png")

    def load_orm_map(self, path):
        self.orm_map = self.load_texture(path if path else None, "assets/textures/EmptyORM.png")

    @staticmethod
    def identity(ctx):
        return Material(ctx, None, None, None, None, 0, 1)