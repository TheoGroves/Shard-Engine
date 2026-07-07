from PIL import Image
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

def load_texture(engine, path, fallback):
    filename = path if path else fallback
    img = Image.open(filename).convert("RGBA")

    if get_asset_type(filename) in [" orm", "_orm"]:
        r, g, b, a = img.split()

        avg_occ = np.asarray(r, dtype=np.uint8).mean()

        if avg_occ < 10:
            print("WARNING: ORM map occlusion is very low, updating to be illuminated.")
            r = r.point(lambda _: 255)
            img = Image.merge("RGBA", (r, g, b, a))

    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    pixels = np.asarray(img, dtype=np.uint8)

    tex = engine.create_texture_rgba(pixels)
    return tex, filename

def save_cooked_tex(src_path, out_path):
    img = Image.open(src_path).convert("RGBA")
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    pixels = np.asarray(img, dtype=np.uint8)

    data = {
        "width": img.width,
        "height": img.height,
        "rgba": pixels.tobytes()
    }

    with open(out_path, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_cooked_tex(engine, path):
    with open(path, "rb") as f:
        data = pickle.load(f)

    pixels = np.frombuffer(
        data["rgba"],
        dtype=np.uint8
    ).reshape((data["height"], data["width"], 4))

    tex = engine.create_texture_rgba(pixels)

    return tex, path

def load_env_map(engine, path):
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

    env_map = engine.create_texture_rgb32f(img)

    return env_map, img, width, height, path

def save_cooked_env_map(img, width, height, out_path):
    data = {
        "width": width,
        "height": height,
        "rgb": np.asarray(img, dtype=np.float32).tobytes()
    }

    with open(out_path, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_cooked_env_map(engine, path):
    with open(path, "rb") as f:
        data = pickle.load(f)

    pixels = np.frombuffer(
        data["rgb"],
        dtype=np.float32
    ).reshape((data["height"], data["width"], 3))

    tex = engine.create_texture_rgb32f(pixels)

    return tex, path