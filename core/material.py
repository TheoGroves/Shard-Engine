from PIL import Image
import moderngl

class Material:
    def __init__(self, ctx, tex_path, normal_path, heightmap_path, height_scale, roughness, uv_scale):
        self.ctx = ctx
        self.texture = self.load_texture(f"assets/textures/{tex_path}" if tex_path else None, "assets/textures/Empty.png")
        self.normal_map = self.load_texture(f"assets/textures/{normal_path}" if normal_path else None, "assets/textures/EmptyNormal.png")
        self.heightmap = self.load_texture(f"assets/textures/{heightmap_path}" if heightmap_path else None, "assets/textures/EmptyHeightmap.png")
        self.height_scale = height_scale
        self.roughness = roughness
        self.uv_scale = uv_scale

    def load_texture(self, path, fallback):
        img = Image.open(path if path else fallback).convert("RGBA")
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        tex = self.ctx.texture(img.size, 4, img.tobytes())
        tex.build_mipmaps()
        tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)

        return tex