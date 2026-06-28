import pygame
import moderngl
from OpenGL import GL
import os
import psutil
import time
import numpy as np
import math

from core import Renderer, RenderPipeline, InputManager, Scene, AssetManager, Engine, Material
from core.components import MeshRenderer, Rigidbody, PlayerController, Input, CapsuleCollider, Transform, Camera, MeshCollider
from core.systems import CollisionSystem, TransformSystem, MeshRendererSystem, InputSystem, PlayerControllerSystem, CameraSystem, MeshColliderSystem
from rendering import ShadowMapper, ColliderDebugger, generate_skybox, SkyboxSettings
from ui import UIRenderer, EditorUI
from maths import get_view_matrix, Vec3

engine_start = time.perf_counter()

# Engine Variables
PLAY_MODE = True
WIREFRAME = False
DEBUG_COLLIDERS = False
GRAVITY = -9.81
PROCEDURAL_SKYBOX = True
GL_GPU_MEMORY_INFO_TOTAL_AVAILABLE_MEMORY_NVX = 0x9048

# Setup pygame
t = time.perf_counter()
pygame.init()

screen_width, screen_height = 2560, 1440
screen = pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

ld = Vec3(1.0, 0.5, 0.0)
light_dir = ld.to_tuple()

world_time = 75
print(f"Pygame setup took {(time.perf_counter()-t)*1000:.1f}ms")

# Setup OpenGL Context
t = time.perf_counter()
ctx = moderngl.create_context()

print(f"OpenGL Context creation took {(time.perf_counter()-t)*1000:.1f}ms")

# Setup Engine Systems
t = time.perf_counter()

renderer = Renderer(ctx, screen_width, screen_height)
renderer.build_pipeline()

shadow_mapper = ShadowMapper(ctx, tuple(-x for x in light_dir), 4096)

asset_manager = AssetManager(ctx)

input_manager = InputManager()

transform_system = TransformSystem(None)
mesh_renderer_system = MeshRendererSystem(None, renderer, asset_manager)
mesh_collider_system = MeshColliderSystem(None, renderer, asset_manager)

print(f"Systems creation took {(time.perf_counter()-t)*1000:.1f}ms")

# Create scene and create Engine
t = time.perf_counter()
scene = Scene("Warehouse", renderer, shadow_mapper, asset_manager)
transform_system.em = scene.em
mesh_renderer_system.em = scene.em
mesh_collider_system.em = scene.em

engine = Engine(ctx, scene, renderer, mesh_collider_system, PLAY_MODE)
print(f"Engine Creation {(time.perf_counter()-t)*1000:.1f}ms")

# Load HDRI into renderer
t = time.perf_counter()
renderer.load_env_map("assets/textures/Day-HDRI.exr", asset_manager)
print(f"Environment map loaded in {(time.perf_counter()-t)*1000:.1f}ms")

# Generate skybox from skybox settings and directional light
t = time.perf_counter()
skybox_settings = SkyboxSettings(PROCEDURAL_SKYBOX, light_dir, (1.0, 1.0, 1.0))
skybox, skybox_prog = generate_skybox(ctx, skybox_settings)
print(f"Skybox generation completed in {(time.perf_counter()-t)*1000:.1f}ms")

# Load main scene
cam_t, cam, player_controller_system, player_eid, bvh, triangles = engine.initialize()

# Create final systems
t = time.perf_counter()
collider_debugger = ColliderDebugger(ctx, scene.em, mesh_collider_system)

collision_system = CollisionSystem(scene.em)
input_system = InputSystem(scene.em)
camera_system = CameraSystem(scene.em, transform_system)

dt=0
dt_real=0
fps=0

print(f"Systems finalisation took {(time.perf_counter()-t)*1000:.1f}ms")

# Get profiling data
t = time.perf_counter()
process = psutil.Process(os.getpid())
total_ram = psutil.virtual_memory().total
TOTAL_KB = GL.glGetIntegerv(GL_GPU_MEMORY_INFO_TOTAL_AVAILABLE_MEMORY_NVX)
print(f"Memory profiling setup took {(time.perf_counter()-t)*1000:.1f}ms")

# Setup UI
t = time.perf_counter()
ui_renderer = UIRenderer(ctx, (screen_width, screen_height))
editor_ui = EditorUI(ui_renderer, engine)
editor_ui.initialize(skybox_settings)
print(f"UI setup took {(time.perf_counter()-t)*1000:.1f}ms")

# Setup render pipeline
t = time.perf_counter()
render_pipeline = RenderPipeline(ctx, renderer, skybox, skybox_prog, skybox_settings, shadow_mapper, collider_debugger, ui_renderer, mesh_renderer_system)
print(f"Render pipeline generated in {(time.perf_counter()-t)*1000:.1f}ms")

# Backup/update scene
t = time.perf_counter()
engine.save()
print(f"Scene backed up in {(time.perf_counter()-t)*1000:.1f}ms")

print(f"Engine loaded in {(time.perf_counter()-engine_start)*1000:.1f}ms")

while True:
    start = time.perf_counter()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    # Handle player inputs and movement
    input_manager.update()
    keys = input_manager.current_keys
    
    input_system.update()
    player_controller_system.update(dt, triangles, bvh, GRAVITY)

    camera_system.update(keys, dt, ui_renderer)

    # Get current RAM usage and warn if using over half of available memory
    curr_mem_usage = process.memory_info().rss / 1048576

    ram_use = process.memory_info().rss/total_ram
    if ram_use > 0.5:
        print(f"WARNING: {ram_use * 100:.1f}% of RAM used")

    # Update scene when reloaded
    packed_state = editor_ui.update(PLAY_MODE, fps, dt, dt_real, curr_mem_usage, TOTAL_KB, camera_system, skybox_settings)
    if packed_state:
        cam_t, cam, player_controller_system, player_eid, bvh, triangles = packed_state

    world_time = math.degrees(editor_ui.sky_ui["sun_rad"].update())

    # Enter and exit Play Mode
    if input_manager.is_key_just_pressed(pygame.K_c):
        PLAY_MODE = not PLAY_MODE
        player_controller_system.play_mode = PLAY_MODE

    # Engine debug view modes
    if input_manager.is_key_just_pressed(pygame.K_x):
        WIREFRAME = not WIREFRAME

    if input_manager.is_key_just_pressed(pygame.K_v):
        DEBUG_COLLIDERS = not DEBUG_COLLIDERS
        for c_eid in scene.em.query("MeshCollider"):
            c = scene.em.entities[c_eid].components["MeshCollider"]
            c.debug = DEBUG_COLLIDERS
    
    # Update directional light
    ld.euler_to_vector(90, world_time, 0)

    light_dir = ld.to_tuple()
    skybox_settings.sun_dir = light_dir

    # Update player model in Play Mode
    if PLAY_MODE:
        transform_system.set_pos(player_eid, cam_t.pos)

    # Place a temp model at mouse position in editor mode with raycast TODO: Implement proper asset placement rather than Suzanne
    if not PLAY_MODE and input_manager.is_mouse_just_pressed(2):
        mx, my = pygame.mouse.get_pos()
        hit_pos, _ = renderer.screen_to_world(mx, my, bvh, triangles)
        if isinstance(hit_pos, np.ndarray):
            eid, entity = scene.em.create_entity()
            scene.em.add_component(eid, Transform(hit_pos))
            scene.em.add_component(eid, MeshRenderer(None, None, None))
            mesh_renderer_system.load_model(eid, "assets/models/Suzanne.obj", shadow_mapper)
            mesh_renderer_system.set_material(eid, Material(ctx, asset_manager, height_scale=0, uv_scale=8))

    transform_system.update()

    # Render Scene    
    ctx.wireframe = WIREFRAME
    renderer.view = get_view_matrix(cam_t)
    shadow_mapper.update(cam_t, skybox_settings.sun_dir)
    render_pipeline.render_frame(scene)

    # Profiling
    pygame.display.set_caption(f"Shard Engine")

    pygame.display.flip()

    dt_real = time.perf_counter()-start
    dt = clock.tick(60)/1000
    fps = clock.get_fps()