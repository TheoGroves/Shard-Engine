import time
import ctypes

from maths.python import Vec3, Mat4, model_matrix, length, normalize

from core import AssetManager, EntityManager
from rendering import RenderEngine, Camera, update_camera_vectors, PBRMaterial, SkyboxMaterial

from core.systems import TransformSystem, MeshRendererSystem, CollisionSystem
from core.components import Transform, MeshRenderer, Skybox

from core.logger import *

from collisions import BVH

ENGINE_VERSION = "0.0.1"

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

# Setup camera controller
move_speed = 5
mouse_sensitivity = 0.0025

# Build collision BVH
bvh = BVH()
triangles = collision_system.get_collision_triangles(bvh)

dt = 1/60
try:
    while not render_engine.should_close():
        s = time.perf_counter()
        player_input = render_engine.get_input()

        move_dir = Vec3(0,0,0)

        if player_input.sprint:
            move_speed = 10
        else:
            move_speed = 5

        if player_input.forward:
            move_dir = move_dir + cam.forward

        if player_input.backward:
            move_dir = move_dir - cam.forward

        if player_input.right:
            move_dir = move_dir + cam.right

        if player_input.left:
            move_dir = move_dir - cam.right

        if player_input.up:
            move_dir = move_dir + cam.world_up

        if player_input.down:
            move_dir = move_dir - cam.world_up

        if length(move_dir) > 0.0:
            cam.position = cam.position + normalize(move_dir) * move_speed * dt;

        cam.rotation.y += player_input.mouse_dx * mouse_sensitivity;
        cam.rotation.x += player_input.mouse_dy * mouse_sensitivity;

        if cam.rotation.x > 1.5: cam.rotation.x = 1.5
        if cam.rotation.x < -1.5: cam.rotation.x = -1.5

        update_camera_vectors(cam)

        mesh_renderer_system.update(render_engine, light_dir, cam)

        collision_system.update()

        dt = time.perf_counter() - s
        #log_trace(f"{1/dt:.1f} fps")
        time.sleep(max(0, 1/60-dt))
        dt = time.perf_counter() - s
finally:
    render_engine.shutdown()