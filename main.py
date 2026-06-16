import pygame
import moderngl
from OpenGL import GL
import os
import psutil
import time

from core import Renderer, RenderPipeline, InputManager, Scene, AssetManager, Engine
from core.components import MeshRenderer, Rigidbody, PlayerController, Input, CapsuleCollider, Transform, Camera, MeshCollider
from core.systems import CollisionSystem, TransformSystem, MeshRendererSystem, InputSystem, PlayerControllerSystem, CameraSystem, MeshColliderSystem
from rendering import ShadowMapper, ColliderDebugger, generate_skybox, SkyboxSettings
from ui import UIRenderer, EditorUI
from maths import get_view_matrix, Vec3

engine_start = time.perf_counter()

PLAY_MODE = True

WIREFRAME = False

DEBUG_COLLIDERS = False
GRAVITY = -9.81

PROCEDURAL_SKYBOX = True

GL_GPU_MEMORY_INFO_TOTAL_AVAILABLE_MEMORY_NVX = 0x9048

t = time.perf_counter()
pygame.init()

screen_width, screen_height = 2560, 1440
screen = pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

ld = Vec3(1.0, 0.5, 0.0)
light_dir = ld.to_tuple()

world_time = 320
print(f"Pygame setup took {(time.perf_counter()-t)*1000:.1f}ms")

t = time.perf_counter()
ctx = moderngl.create_context()

print(f"OpenGL Context creation took {(time.perf_counter()-t)*1000:.1f}ms")

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

t = time.perf_counter()
scene = Scene("Warehouse", renderer, shadow_mapper, asset_manager)
transform_system.em = scene.em
mesh_renderer_system.em = scene.em
mesh_collider_system.em = scene.em

engine = Engine(ctx, scene, renderer, mesh_collider_system, PLAY_MODE)
print(f"Engine Creation {(time.perf_counter()-t)*1000:.1f}ms")

t = time.perf_counter()
renderer.load_env_map("assets/textures/Day-HDRI.exr")
print(f"Environment map loaded in {(time.perf_counter()-t)*1000:.1f}ms")

t = time.perf_counter()
skybox_settings = SkyboxSettings(PROCEDURAL_SKYBOX, light_dir, (1.0, 1.0, 1.0))
skybox, skybox_prog = generate_skybox(ctx, skybox_settings)
print(f"Skybox generation completed in {(time.perf_counter()-t)*1000:.1f}ms")

cam_t, cam, player_controller_system, player_eid, grid, triangles = engine.initialize()

t = time.perf_counter()
collider_debugger = ColliderDebugger(ctx, scene.em, mesh_collider_system)

collision_system = CollisionSystem(scene.em)
input_system = InputSystem(scene.em)
camera_system = CameraSystem(scene.em, transform_system)

dt=0
dt_real=0
fps=0

print(f"Systems finalisation took {(time.perf_counter()-t)*1000:.1f}ms")

t = time.perf_counter()
process = psutil.Process(os.getpid())
total_ram = psutil.virtual_memory().total
TOTAL_KB = GL.glGetIntegerv(GL_GPU_MEMORY_INFO_TOTAL_AVAILABLE_MEMORY_NVX)
print(f"Memory profiling setup took {(time.perf_counter()-t)*1000:.1f}ms")

t = time.perf_counter()
ui_renderer = UIRenderer(ctx, (screen_width, screen_height))
editor_ui = EditorUI(ui_renderer, engine)
editor_ui.initialize()
print(f"UI setup took {(time.perf_counter()-t)*1000:.1f}ms")

t = time.perf_counter()
render_pipeline = RenderPipeline(ctx, renderer, skybox, skybox_prog, skybox_settings, shadow_mapper, collider_debugger, ui_renderer, mesh_renderer_system)
print(f"Render pipeline generated in {(time.perf_counter()-t)*1000:.1f}ms")

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

    input_manager.update()
    keys = input_manager.current_keys
    
    input_system.update()
    player_controller_system.update(dt, triangles, grid, GRAVITY)
    
    curr_mem_usage = process.memory_info().rss / 1048576

    packed_state = editor_ui.update(PLAY_MODE, fps, dt, dt_real, curr_mem_usage, TOTAL_KB, camera_system)
    if packed_state:
        cam_t, cam, player_controller_system, player_eid, grid, triangles = packed_state


    ram_use = process.memory_info().rss/total_ram
    if ram_use > 0.5:
        print(f"WARNING: {ram_use * 100:.1f}% of RAM used")

    if input_manager.is_key_just_pressed(pygame.K_c):
        PLAY_MODE = not PLAY_MODE
        player_controller_system.play_mode = PLAY_MODE

    if input_manager.is_key_just_pressed(pygame.K_x):
        WIREFRAME = not WIREFRAME

    if input_manager.is_key_just_pressed(pygame.K_v):
        DEBUG_COLLIDERS = not DEBUG_COLLIDERS
        for c_eid in scene.em.query("MeshCollider"):
            c = scene.em.entities[c_eid].components["MeshCollider"]
            c.debug = DEBUG_COLLIDERS
    
    ld.euler_to_vector(90, world_time, 0)

    light_dir = ld.to_tuple()
    skybox_settings.sun_dir = light_dir

    #world_time += 4*dt

    ctx.wireframe = WIREFRAME

    camera_system.update(keys, dt, ui_renderer)

    if PLAY_MODE:
        transform_system.set_pos(player_eid, cam_t.pos)
    
    transform_system.update()
    
    renderer.view = get_view_matrix(cam_t)

    shadow_mapper.update(cam_t, skybox_settings.sun_dir)

    render_pipeline.render_frame(scene)

    pygame.display.set_caption(f"Engine | {fps:.0f}fps")

    pygame.display.flip()

    dt_real = time.perf_counter()-start
    dt = clock.tick(60)/1000
    fps = clock.get_fps()