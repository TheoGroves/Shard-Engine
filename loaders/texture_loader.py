from PIL import Image
import moderngl
import os
import pickle

def get_asset_type(filename):
    name = os.path.splitext(filename)[0].lower()

    for suffix in [" base", " normal", " orm", " heightmap", "_base", "_normal", "_orm", "_heightmap"]:
        if name.endswith(suffix):
            return suffix

def load_texture(ctx, path, fallback):
    i = Image.open(path if path else fallback).convert("RGBA")

    if get_asset_type(path if path else fallback) in [" orm", "_orm"]:
        r, g, b, a = i.split()

        pixels = list(r.getdata())
        avg_occ = sum(pixels) / len(pixels)

        if avg_occ < 10:
            print("WARNING: ORM map occlusion is very low, updating to be illuminated.")
            r = r.point(lambda _: 255)

            out = Image.merge("RGBA", (r, g, b, a))
            out.save(path)

    img = Image.open(path if path else fallback).convert("RGBA")

    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    tex = ctx.texture(img.size, 4, img.tobytes())
    tex.build_mipmaps()
    tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)

    return tex, path if path else fallback

def save_cooked_tex(src_path, out_path):
    img = Image.open(src_path).convert("RGBA")
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    data = {
        "width": img.width,
        "height": img.height,
        "rgba": img.tobytes()
    }

    with open(out_path, "wb") as f:
        pickle.dump(data, f)

def load_cooked_tex(ctx, path):
    with open(path, "rb") as f:
        data = pickle.load(f)

    tex = ctx.texture(
        (data["width"], data["height"]),
        4,
        data["rgba"]
    )
    tex.build_mipmaps()
    tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)

    return tex, path