import traceback
import time
import ctypes

from maths.python import Vec3

from core import AssetManager, EntityManager
from rendering import RenderEngine, PBRMaterial, SkyboxMaterial, Viewport

from core.systems import TransformSystem, MeshRendererSystem, CollisionSystem, PhysicsSystem, CameraSystem, FlyControllerSystem
from core.components import Name, Transform, MeshRenderer, MeshCollider, LinearBody, CapsuleCollider, Camera, FlyController

from core.logger import Logger

from collisions import BVH

from editor import Console, ViewportUI, Hierarchy, Inspector, Profiler

def safe_update(name, callback, *args):
    try:
        callback(*args)
    except Exception as e:
        logger.log_error(f"Unhandled exception in system {name}:\n{traceback.format_exc()}")

try:
    ENGINE_VERSION = "0.2.7"

    # Setup Console
    console = Console()
    logger = Logger(console)

    logger.log_info(f"SHARD ENGINE v{ENGINE_VERSION}")

    # Engine Variables
    PLAY_MODE = True

    user32 = ctypes.windll.user32

    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # Setup Shard Renderer
    render_engine = RenderEngine()
    render_engine.initialize(screen_width, screen_height, "Shard Engine")
    render_engine.hide_mouse()
    console.set_render_engine(render_engine)

    viewport = Viewport()
    viewport.create(1280, 720)

    # Setup systems
    entity_manager = EntityManager()
    asset_manager = AssetManager(render_engine, logger)
    asset_manager.load_textures("assets/textures", logger)
    asset_manager.load_env_maps("assets/textures", logger)

    transform_system = TransformSystem(entity_manager, logger)
    mesh_renderer_system = MeshRendererSystem(entity_manager, asset_manager, logger)
    collision_system = CollisionSystem(entity_manager, asset_manager)
    physics_system = PhysicsSystem(entity_manager)
    camera_system = CameraSystem(entity_manager)
    fly_controller_system = FlyControllerSystem(entity_manager, render_engine)

    # Setup UI
    viewport_ui = ViewportUI(render_engine)
    hierarchy = Hierarchy(render_engine, entity_manager, transform_system)
    inspector = Inspector(render_engine, entity_manager, hierarchy, asset_manager)
    profiler = Profiler(render_engine)

except Exception as e:
    logger.log_fatal(f"Core engine initialization failed:\n{traceback.format_exc()}")

try:
    # Load Scene
    skybox_eid, _ = entity_manager.create_entity()
    entity_manager.add_component(skybox_eid, Name("Skybox", "Skybox"))
    entity_manager.add_component(skybox_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
    entity_manager.add_component(skybox_eid, MeshRenderer())
    mesh_renderer_system.set_mesh(skybox_eid, "assets/models/Cube.obj")
    mesh_renderer_system.set_material(skybox_eid, SkyboxMaterial(render_engine, asset_manager, "assets/textures/Day-HDRI.exr"))

    player_eid, _ = entity_manager.create_entity()
    entity_manager.add_component(player_eid, Name("Player"))
    entity_manager.add_component(player_eid, Transform(Vec3(0,10,0), Vec3(0,0,0), Vec3(1,1,1)))
    entity_manager.add_component(player_eid, MeshRenderer())
    entity_manager.add_component(player_eid, LinearBody())
    entity_manager.add_component(player_eid, CapsuleCollider(2, 1, 0))
    mesh_renderer_system.set_mesh(player_eid, "assets/models/Player.obj")
    mesh_renderer_system.set_material(player_eid, PBRMaterial(render_engine, asset_manager, logger, "assets/textures/Empty.png", "assets/textures/EmptyNormal.png", "assets/textures/EmptyHeightmap.png", "assets/textures/EmptyORM.png"))

    cam_eid, _ = entity_manager.create_entity()
    entity_manager.add_component(cam_eid, Name("Camera", "MainCamera"))
    entity_manager.add_component(cam_eid, Transform(Vec3(0,5,0), Vec3(0,0,0), Vec3(1,1,1)))
    entity_manager.add_component(cam_eid, Camera(True))
    entity_manager.add_component(cam_eid, FlyController())

    warehouse_eid, _ = entity_manager.create_entity()
    entity_manager.add_component(warehouse_eid, Name("Warehouse"))
    entity_manager.add_component(warehouse_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
    entity_manager.add_component(warehouse_eid, MeshRenderer())
    entity_manager.add_component(warehouse_eid, MeshCollider(None))
    mesh_renderer_system.set_mesh(warehouse_eid, "assets/models/WarehouseCollider.obj")
    mesh_renderer_system.set_material(warehouse_eid, PBRMaterial(render_engine, asset_manager, logger, "assets/textures/Empty.png", "assets/textures/EmptyNormal.png", "assets/textures/EmptyHeightmap.png", "assets/textures/EmptyORM.png"))
    collision_system.set_mesh(warehouse_eid, "assets/models/WarehouseCollider.obj")

    light_dir = Vec3(-0.3, -1.0, -0.2)

    # Build collision BVH
    bvh = BVH()
    triangles = collision_system.get_collision_triangles(bvh)
except Exception as e:
    logger.log_fatal(f"Scene loading failed:\n{traceback.format_exc()}")

dt = 1/60

try:
    while not render_engine.should_close():
        s = time.perf_counter()
        player_input = render_engine.get_input()

        safe_update("FlyController", fly_controller_system.update, player_input, dt)

        safe_update("Physics", physics_system.update, -9.81, dt)

        safe_update("Collision", collision_system.update)

        safe_update("Transform", transform_system.update)

        safe_update("Camera", camera_system.update, logger)

        safe_update("MeshRenderer", mesh_renderer_system.update, render_engine, light_dir, camera_system.render_camera, viewport)

        safe_update("ConsoleUI", console.update, logger)
        safe_update("ViewportUI", viewport_ui.update, viewport, camera_system.render_camera)
        safe_update("HierarchyUI", hierarchy.update)
        safe_update("InspectorUI", inspector.update, logger)
        safe_update("ProfilerUI", profiler.update, dt)

        render_engine.end_frame()

        dt = time.perf_counter() - s
        time.sleep(max(0, 1/60-dt))
        dt = time.perf_counter() - s
finally:
    render_engine.shutdown()
    console.cleanup()