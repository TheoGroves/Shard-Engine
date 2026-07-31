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

def load_texture(render_engine, path, fallback, logger):
    filename = path if path else fallback
    img = Image.open(filename).convert("RGBA")

    if get_asset_type(filename) in [" orm", "_orm"]:
        r, g, b, a = img.split()

        avg_occ = np.asarray(r, dtype=np.uint8).mean()

        if avg_occ < 10:
            logger.log_warning("ORM map occlusion is very low, updating to be illuminated.")
            r = r.point(lambda _: 255)
            img = Image.merge("RGBA", (r, g, b, a))

    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    pixels = np.asarray(img, dtype=np.uint8)

    tex = render_engine.create_texture_rgba(pixels)
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

def load_cooked_tex(render_engine, path):
    with open(path, "rb") as f:
        data = pickle.load(f)

    pixels = np.frombuffer(
        data["rgba"],
        dtype=np.uint8
    ).reshape((data["height"], data["width"], 4))

    tex = render_engine.create_texture_rgba(pixels)

    return tex, path

def direction_to_uv(d):
    x,y,z = d

    u = np.arctan2(z, x) / (2 * np.pi) + 0.5
    v = np.arcsin(np.clip(y, -1, 1)) / np.pi + 0.5

    return np.array([u, v])

def uv_to_direction(x, y, width, height):
    u = (x / width) * 2.0 * np.pi - np.pi
    v = (y / height) * np.pi - np.pi * 0.5

    return np.array([
        np.cos(v) * np.cos(u),
        np.sin(v), 
        np.cos(v) * np.sin(u)
    ])

def cosine_sample_hemisphere(n):
    r1 = np.random.random()
    r2 = np.random.random()

    phi = 2.0 * np.pi * r1

    x = np.cos(phi) * np.sqrt(r2)
    y = np.sqrt(1.0 - r2)

    z = np.sin(phi) * np.sqrt(r2)

    up = np.array([0,1,0])

    if abs(n[1]) > 0.99:
        up = np.array([1,0,0])

    tangent = np.cross(up, n)
    tangent /= np.linalg.norm(tangent)

    bitangent = np.cross(n,tangent)

    return tangent*x + n*y + bitangent*z 

def generate_irradiance(env, width, height, samples=128):
    output = np.zeros((height, width, 3), dtype=np.float32)

    for y in range(height):
        for x in range(width):
            n = uv_to_direction(x,y,width,height)

            n /= np.linalg.norm(n)

            colour = np.zeros(3)
            weight = 0.0

            for _ in range(samples):
                l = cosine_sample_hemisphere(n)

                ndotl = max(np.dot(n, l), 0.0)

                colour += sample_env(env, l) * ndotl
                weight += ndotl

            output[y, x] = colour / max(weight, 1e-6)

    return output

def sample_env(env, direction):
    uv = direction_to_uv(direction)

    x = int(uv[0] * env.shape[1]) % env.shape[1]
    y = np.clip(int(uv[1] * env.shape[0]), 0, env.shape[0] - 1)

    return env[y,x]

def load_env_map(render_engine, path):
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

    env_map = render_engine.create_texture_rgb32f(img)

    return env_map, img, width, height, path

def save_cooked_env_map(img, width, height, irr_width, irr_height, irradiance, out_path):
    data = {
        "width": width,
        "height": height,
        "rgb": np.asarray(img, dtype=np.float32).tobytes(),

        "irr_width": irr_width,
        "irr_height": irr_height,
        "irr_rgb": irradiance.astype(np.float32).tobytes()
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

    irr = np.frombuffer(
        data["irr_rgb"],
        dtype=np.float32
    ).reshape((data["irr_height"], data["irr_width"], 3))

    tex = engine.create_texture_rgb32f(pixels)
    irr_tex = engine.create_texture_rgb32f(irr)

    return tex, irr_tex, path

def load_icon(engine, path):
    img = Image.open(path).convert("RGBA")

    pixels = np.asarray(img, dtype=np.uint8)

    engine.set_icon(img.width, img.height, pixels)