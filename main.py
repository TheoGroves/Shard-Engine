import time

from core import AssetManager, EntityManager
from rendering import RenderEngine, Camera, PlayerController, Mat4, model_matrix, Vec3, PBRMaterial, SkyboxMaterial

from core.systems import TransformSystem, MeshRendererSystem
from core.components import Transform, MeshRenderer, Skybox

# Engine Variables
PLAY_MODE = True

screen_width, screen_height = 2560, 1440

# Setup Shard Renderer
render_engine = RenderEngine()
render_engine.initialize(screen_width, screen_height, "Shard Renderer")
render_engine.hide_mouse()

# Setup systems
entity_manager = EntityManager()
asset_manager = AssetManager(render_engine)

transform_system = TransformSystem(entity_manager)
mesh_renderer_system = MeshRendererSystem(entity_manager, asset_manager)

# Load Scene
skybox_eid, _ = entity_manager.create_entity()
entity_manager.add_component(skybox_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
entity_manager.add_component(skybox_eid, MeshRenderer())
entity_manager.add_component(skybox_eid, Skybox())
mesh_renderer_system.set_mesh(skybox_eid, "assets/models/Cube.obj")
mesh_renderer_system.set_material(skybox_eid, SkyboxMaterial(render_engine, asset_manager, "assets/textures/Day-HDRI.exr"))

warehouse_eid, _ = entity_manager.create_entity()
entity_manager.add_component(warehouse_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
entity_manager.add_component(warehouse_eid, MeshRenderer())
mesh_renderer_system.set_mesh(warehouse_eid, "assets/models/WarehouseCollider.obj")
mesh_renderer_system.set_material(warehouse_eid, PBRMaterial(render_engine, asset_manager, "assets/textures/Empty.png", "assets/textures/EmptyNormal.png", "assets/textures/EmptyHeightmap.png", "assets/textures/EmptyORM.png"))

light_dir = Vec3(-0.3, -1.0, -0.2)
cam = Camera()
controller = PlayerController()

dt = 1/60
try:
    while not render_engine.should_close():
        s = time.perf_counter()
        player_input = render_engine.get_input()
        controller.update(cam, player_input, dt)

        mesh_renderer_system.update(render_engine, light_dir, cam)

        dt = time.perf_counter() - s
        print(1/dt)
        time.sleep(max(0, 1/60-dt))
        dt = time.perf_counter() - s
finally:
    render_engine.shutdown()