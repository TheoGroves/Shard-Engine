import time
import os
import re
from core.game_object import GameObject
from core.transform import Transform
from core.material import Material

def get_asset_key(filename):
    name = os.path.splitext(filename)[0].lower()

    for suffix in [" base", " normal", " orm", " heightmap", "_base", "_normal", "_orm", "_heightmap"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]

    name = name.replace("_", " ")

    name = re.sub(r"\s+", " ", name).strip()

    if name.isdigit():
        return int(name)

    return name

def load_many(ctx, renderer, models_path, textures_path):
    start = time.perf_counter()

    game_objects = {}

    for model in os.listdir(models_path):
        if not model.endswith(".obj"):
            continue

        key = get_asset_key(model)
        model_path = f"{models_path}/{model}"
        name = os.path.splitext(model)[0]

        go = GameObject(name, Transform.identity(), Material.identity(ctx))

        go.load_model(model_path)
        renderer.generate_buffers(go)

        game_objects[key] = go

    materials = {}

    for tex in os.listdir(textures_path):
        key = get_asset_key(tex)

        tex_path = f"{textures_path}/{tex}"

        if key not in materials:
            materials[key] = Material.identity(ctx)

        tex_lower = tex.lower()

        if "base" in tex_lower:
            materials[key].load_base_map(tex_path)
        elif "normal" in tex_lower:
            materials[key].load_normal_map(tex_path)
        elif "orm" in tex_lower:
            materials[key].load_orm_map(tex_path)
        elif "heightmap" in tex_lower:
            materials[key].load_height_map(tex_path)
        else:
            print(f"Unable to determine texture type: {tex}")

    for key in game_objects.keys():
        if key in materials:
            print(f"Loaded material for {key}")
            game_objects[key].material = materials[key]
        
    print(f"Loaded assets in {(time.perf_counter()-start)*1000:.0f}ms")
    return game_objects