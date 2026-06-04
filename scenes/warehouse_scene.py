from core.scene import Scene
from core.transform import Transform
from rendering.skybox import generate_skybox
from collisions.collider import Collider
from importers.asset_importer import load_many

class WarehouseSceneBuilder:
    @staticmethod
    def build(ctx, renderer, shadow_mapper, DEBUG_COLLIDERS):
        scene = Scene("Warehouse", renderer, shadow_mapper)

        loaded_objects = load_many(ctx, renderer, "assets/models/WarehouseModels", "assets/textures/WarehouseTextures")
        for go in loaded_objects.values():
            scene.add(go)

        warehouse_collider = Collider(ctx, "assets/models/WarehouseCollider.obj", DEBUG_COLLIDERS)
        warehouse_collider.set_model(Transform((0,0,0), (0,0,0), (1, 1, 1)))

        scene.add_collider(warehouse_collider)

        renderer.load_env_map("assets/textures/Day-HDRI.exr")
        skybox, skybox_prog = generate_skybox(ctx)

        return scene, skybox, skybox_prog