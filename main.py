import traceback
import time
import ctypes

from maths.python import Vec3, Mat4, model_matrix, length, normalize

from core import AssetManager, EntityManager
from rendering import RenderEngine, Camera, update_camera_vectors, PBRMaterial, SkyboxMaterial

from core.systems import TransformSystem, MeshRendererSystem, CollisionSystem, PhysicsSystem, CameraSystem
from core.components import Transform, MeshRenderer, MeshCollider, Skybox, LinearBody, CapsuleCollider, Camera

from core.logger import *

from collisions import BVH

try:
    ENGINE_VERSION = "0.1.1"

    log_info(f"SHARD ENGINE v{ENGINE_VERSION}")

    # Engine Variables
    PLAY_MODE = True

    user32 = ctypes.windll.user32

    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # Setup Shard Renderer
    render_engine = RenderEngine()
    render_engine.initialize(screen_width, screen_height, "Shard Renderer")
    render_engine.hide_mouse()

    # Setup systems
    entity_manager = EntityManager()
    asset_manager = AssetManager(render_engine)

    transform_system = TransformSystem(entity_manager)
    mesh_renderer_system = MeshRendererSystem(entity_manager, asset_manager)
    collision_system = CollisionSystem(entity_manager, asset_manager)
    physics_system = PhysicsSystem(entity_manager)
    camera_system = CameraSystem(entity_manager)
except Exception as e:
    log_fatal(f"Core engine initialization failed:\n{traceback.format_exc()}")

try:
    # Load Scene
    skybox_eid, _ = entity_manager.create_entity()
    entity_manager.add_component(skybox_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
    entity_manager.add_component(skybox_eid, MeshRenderer())
    entity_manager.add_component(skybox_eid, Skybox())
    mesh_renderer_system.set_mesh(skybox_eid, "assets/models/Cube.obj")
    mesh_renderer_system.set_material(skybox_eid, SkyboxMaterial(render_engine, asset_manager, "assets/textures/Day-HDRI.exr"))

    player_eid, _ = entity_manager.create_entity()
    entity_manager.add_component(player_eid, Transform(Vec3(0,2,0), Vec3(0,0,0), Vec3(1,1,1)))
    entity_manager.add_component(player_eid, MeshRenderer())
    entity_manager.add_component(player_eid, LinearBody())
    entity_manager.add_component(player_eid, CapsuleCollider(2, 1, 0))
    mesh_renderer_system.set_mesh(player_eid, "assets/models/Player.obj")
    mesh_renderer_system.set_material(player_eid, PBRMaterial(render_engine, asset_manager, "assets/textures/Empty.png", "assets/textures/EmptyNormal.png", "assets/textures/EmptyHeightmap.png", "assets/textures/EmptyORM.png"))

    cam_eid, _ = entity_manager.create_entity()
    entity_manager.add_component(cam_eid, Transform(Vec3(0,5,0), Vec3(0,0,0), Vec3(1,1,1)))
    entity_manager.add_component(cam_eid, Camera(True))

    warehouse_eid, _ = entity_manager.create_entity()
    entity_manager.add_component(warehouse_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
    entity_manager.add_component(warehouse_eid, MeshRenderer())
    entity_manager.add_component(warehouse_eid, MeshCollider(None))
    mesh_renderer_system.set_mesh(warehouse_eid, "assets/models/WarehouseCollider.obj")
    mesh_renderer_system.set_material(warehouse_eid, PBRMaterial(render_engine, asset_manager, "assets/textures/Empty.png", "assets/textures/EmptyNormal.png", "assets/textures/EmptyHeightmap.png", "assets/textures/EmptyORM.png"))
    collision_system.set_mesh(warehouse_eid, "assets/models/WarehouseCollider.obj")

    light_dir = Vec3(-0.3, -1.0, -0.2)

    # Setup camera controller
    move_speed = 5
    mouse_sensitivity = 0.0025

    # Build collision BVH
    bvh = BVH()
    triangles = collision_system.get_collision_triangles(bvh)
except Exception as e:
    log_error(f"Scene loading failed:\n{traceback.format_exc()}")

dt = 1/60
try:
    while not render_engine.should_close():
        s = time.perf_counter()
        player_input = render_engine.get_input()

        cam_t = entity_manager.entities[cam_eid].components["Transform"]

        move_dir = Vec3(0,0,0)

        if player_input.sprint:
            move_speed = 10
        else:
            move_speed = 5

        if player_input.forward:
            move_dir = move_dir + camera_system.render_camera.forward

        if player_input.backward:
            move_dir = move_dir - camera_system.render_camera.forward

        if player_input.right:
            move_dir = move_dir + camera_system.render_camera.right

        if player_input.left:
            move_dir = move_dir - camera_system.render_camera.right

        if player_input.up:
            move_dir = move_dir + camera_system.render_camera.world_up

        if player_input.down:
            move_dir = move_dir - camera_system.render_camera.world_up

        if length(move_dir) > 0.0:
            cam_t.pos = cam_t.pos + normalize(move_dir) * move_speed * dt;

        cam_t.rot.y += player_input.mouse_dx * mouse_sensitivity;
        cam_t.rot.x += player_input.mouse_dy * mouse_sensitivity;

        if cam_t.rot.x > 1.5: cam_t.rot.x = 1.5
        if cam_t.rot.x < -1.5: cam_t.rot.x = -1.5

        camera_system.update()

        physics_system.update(-9.81, dt)

        collision_system.update()

        transform_system.update()

        mesh_renderer_system.update(render_engine, light_dir, camera_system.render_camera)

        dt = time.perf_counter() - s
        #log_trace(f"{1/dt:.1f} fps")
        time.sleep(max(0, 1/60-dt))
        dt = time.perf_counter() - s
except Exception as e:
    log_error(f"Unhandled exception in main loop:\n{traceback.format_exc()}")
finally:
    render_engine.shutdown()