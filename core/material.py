from PIL import Image
import moderngl

class Material:
    def __init__(self, ctx, tex_path, normal_path, roughness):
        self.ctx = ctx
        self.texture = self.load_texture(tex_path)
        self.normal_map = self.load_texture(normal_path)
        self.roughness = roughness

    def load_texture(self, path):
        img = Image.open(path).convert("RGBA")
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        tex = self.ctx.texture(img.size, 4, img.tobytes())
        tex.build_mipmaps()
        tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)

        return tex