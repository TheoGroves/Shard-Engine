from PIL import Image
import moderngl

def load_texture(ctx, path, fallback):
    img = Image.open(path if path else fallback).convert("RGBA")
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    tex = ctx.texture(img.size, 4, img.tobytes())
    tex.build_mipmaps()
    tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)

    return tex, path if path else fallback