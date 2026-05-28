import time
import os
import re
from core.game_object import GameObject
from core.transform import Transform
from core.material import Material

def load_many(ctx, renderer, models_path, textures_path):
    start = time.perf_counter()

    game_objects = {}

    for model in os.listdir(models_path):
        if model.endswith(".obj"):
            # find index
            match = re.search(r"\d+", model)

            if match:
                index = int(match.group())
            else:
                print(f"Warning: No index found for {model} at {models_path}")
                continue

            # generate gameobject, model and buffers
            model_path = f"{models_path}/{model}"
            name = os.path.splitext(model)[0]

            go = GameObject(name, Transform((0,0,0), (0,0,0)), Material(ctx, None, None, None, 0, 256, 8))
            go.load_model(model_path)
            renderer.generate_buffers(go)

            game_objects[index] = go


    materials = {}

    for tex in os.listdir(textures_path):
        # find index
        match = re.search(r"\d+", tex)

        if match:
            index = int(match.group())
        else:
            print(f"Warning: No index found for {tex} at {textures_path}")
            continue

        tex_path = f"{textures_path}/{tex}"

        # generate material if not already generated
        if index not in materials:
            materials[index] = Material(ctx, None, None, None, 0, 256, 1)

        # determine tex type
        if "base" in tex.lower():
            materials[index].load_base_map(tex_path)
        elif "normal" in tex.lower():
            materials[index].load_normal_map(tex_path)
        else:
            print("Unable to determine texture type")

    for key in game_objects.keys():
        if key in materials:
            game_objects[key].material = materials[key]
        
    print(f"Loaded assets in {(time.perf_counter()-start)*1000:.0f}ms")
    return game_objects