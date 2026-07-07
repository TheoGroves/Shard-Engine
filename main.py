import time

from core import Renderer, RenderPipeline, InputManager, Scene, AssetManager, Engine, Material
from core.components import MeshRenderer, Rigidbody, PlayerController, Input, CapsuleCollider, Transform, Camera, MeshCollider
from core.systems import CollisionSystem, TransformSystem, MeshRendererSystem, InputSystem, PlayerControllerSystem, CameraSystem, MeshColliderSystem
from rendering import RenderEngine, Camera, PlayerController, Mat4, Vec3, PBRMaterial, SkyboxMaterial

# Engine Variables
PLAY_MODE = True
GRAVITY = -9.81

screen_width, screen_height = 2560, 1440

# Setup Shard Renderer
render_engine = RenderEngine()
render_engine.initialize(screen_width, screen_height, "Shard Renderer")
render_engine.hide_mouse()

# Setup systems
asset_manager = AssetManager(render_engine)

# Load Scene
skybox = asset_manager.get_mesh("assets/models/Cube.obj")
skybox_mat = SkyboxMaterial(render_engine, asset_manager, "assets/textures/Day-HDRI.exr")

warehouse = asset_manager.get_mesh("assets/models/WarehouseCollider.obj")
warehouse_mat = PBRMaterial(render_engine, asset_manager, "assets/textures/Empty.png", "assets/textures/EmptyNormal.png", "assets/textures/EmptyHeightmap.png", "assets/textures/EmptyORM.png")

light_dir = Vec3(-0.3, -1.0, -0.2)
cam = Camera()
controller = PlayerController()

dt = 1/60
try:
    while not render_engine.should_close():
        s = time.perf_counter()
        player_input = render_engine.get_input()
        controller.update(cam, player_input, dt)

        warehouse_mat.update(render_engine, cam, light_dir)
        skybox_mat.update(render_engine, cam)

        render_engine.begin_shadows(Vec3(-light_dir.x, -light_dir.y, -light_dir.z), cam.position)
        render_engine.draw_shadow(warehouse, Mat4.identity())
        render_engine.end_shadows()

        render_engine.begin_frame()
        render_engine.disable_depth_test()
        render_engine.disable_cull_face()
        render_engine.draw_mesh(skybox, skybox_mat.material, Mat4.identity())
        render_engine.enable_depth_test()
        render_engine.enable_cull_face()
        render_engine.draw_mesh(warehouse, warehouse_mat.material, Mat4.identity())
        render_engine.end_frame()

        dt = time.perf_counter() - s
        time.sleep(max(0, 1/60-dt))
        dt = time.perf_counter() - s
finally:
    render_engine.shutdown()