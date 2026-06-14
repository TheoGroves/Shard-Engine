from core.scene import Scene
from core.components import Transform, MeshCollider
from core.systems import TransformSystem, MeshRendererSystem, MeshColliderSystem
from rendering.skybox import generate_skybox
from importers.asset_importer import load_many

class WarehouseSceneBuilder:
    @staticmethod
    def build(ctx, renderer, shadow_mapper, DEBUG_COLLIDERS, ts: TransformSystem, mrs: MeshRendererSystem, mcs: MeshColliderSystem):
        scene = Scene("Warehouse", renderer, shadow_mapper)
        ts.em = scene.em
        mrs.em = scene.em
        mcs.em = scene.em

        load_many(ctx, shadow_mapper, "assets/models/WarehouseModels", "assets/textures/WarehouseTextures", scene.em, ts, mrs)

        collider_eid = scene.em.create_entity()
        scene.em.add_component(collider_eid, Transform.identity())
        scene.em.add_component(collider_eid, MeshCollider(None, False))

        mcs.load_model(collider_eid, "assets/models/WarehouseCollider.obj")

        renderer.load_env_map("assets/textures/Day-HDRI.exr")
        skybox, skybox_prog = generate_skybox(ctx)

        return scene, skybox, skybox_prog