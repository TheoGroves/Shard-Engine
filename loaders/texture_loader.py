from PIL import Image
import moderngl
import os
import pickle
import OpenEXR
import Imath
import numpy as np

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

def load_env_map(ctx, path):
    exr = OpenEXR.InputFile(path)
    dw = exr.header()['dataWindow']

    width = dw.max.x - dw.min.x + 1
    height = dw.max.y - dw.min.y + 1

    pt = Imath.PixelType(Imath.PixelType.FLOAT)

    r = np.frombuffer(exr.channel('R', pt), dtype=np.float32)
    g = np.frombuffer(exr.channel('G', pt), dtype=np.float32)
    b = np.frombuffer(exr.channel('B', pt), dtype=np.float32)

    img = np.stack([r, g, b], axis=-1)
    img = img.reshape((height, width, 3))
    img = np.flipud(img)

    env_map = ctx.texture(size=(width, height), components=3, data=img.tobytes(), dtype='f4')

    return env_map, img, width, height, path

def save_cooked_env_map(img, width, height, out_path):
    data = {
        "width": width,
        "height": height,
        "rgb": img.tobytes()
    }

    with open(out_path, "wb") as f:
        pickle.dump(data, f)

def load_cooked_env_map(ctx, path):
    with open(path, "rb") as f:
        data = pickle.load(f)

    tex = ctx.texture(
        (data["width"], data["height"]), 
        3, 
        data["rgb"], 
        dtype='f4'
    )

    return tex, path
