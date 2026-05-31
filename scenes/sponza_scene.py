from core.scene import Scene
from core.transform import Transform
from core.material import Material
from core.game_object import GameObject
from rendering.skybox import generate_skybox
from importers.asset_importer import load_many
from collisions.collider import Collider

class SponzaSceneBuilder:
    @staticmethod
    def build(ctx, renderer, shadow_mapper, DEBUG_COLLIDERS):
        scene = Scene("Sponza", renderer, shadow_mapper)
        loaded_objects = load_many(ctx, renderer, "assets/models/SponzaModels", "assets/textures/SponzaTextures")
        for go in loaded_objects.values():
            scene.add(go)

        sponza_collider = Collider(ctx, "assets/models/SponzaCollider.obj", DEBUG_COLLIDERS)
        sponza_collider.set_model(Transform.identity())

        bunny = GameObject("Bunny", Transform((0, 0, 0), (0,0,0), (0.5,0.5,0.5)), Material(ctx, None, None, None, None, 0, 16))
        bunny.load_model("assets/models/StanfordBunny.obj")

        bunny_collider = Collider(ctx, "assets/models/StanfordBunnyCollider.obj", DEBUG_COLLIDERS)
        bunny_collider.set_model(Transform((0,0,0), (0,0,0), (0.5, 0.5, 0.5)))

        scene.add(bunny)

        scene.add_collider(sponza_collider)
        scene.add_collider(bunny_collider)

        renderer.load_env_map("assets/textures/Day-HDRI.exr")
        skybox, skybox_prog = generate_skybox(ctx)

        return scene, skybox, skybox_prog