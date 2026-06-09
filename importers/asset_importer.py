import time
import os
import re
from core.material import Material
from core.components import Transform, MeshRenderer
from ecs import EntityManager
from core.systems import TransformSystem, MeshRendererSystem

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

def load_many(ctx, shadow_mapper, models_path, textures_path, em: EntityManager, ts: TransformSystem, mrs: MeshRendererSystem):
    start = time.perf_counter()

    eids = {}

    for model in os.listdir(models_path):
        if not model.endswith(".obj"):
            continue

        key = get_asset_key(model)
        model_path = f"{models_path}/{model}"

        eid = em.create_entity()
        em.add_component(eid, Transform.identity())
        em.add_component(eid, MeshRenderer(None, None, Material.identity(ctx)))
        mrs.load_model(eid, model_path, shadow_mapper)

        eids[key] = eid

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

    for key in eids.keys():
        if key in materials:
            print(f"Loaded material for {key}")
            mrs.set_material(eids[key], materials[key])
        
    print(f"Loaded assets in {(time.perf_counter()-start)*1000:.0f}ms")