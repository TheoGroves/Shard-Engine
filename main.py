import pygame
import moderngl
from OpenGL import GL
import os
import psutil
import time

from core import Renderer, RenderPipeline, InputManager, Scene
from core.components import MeshRenderer, Rigidbody, PlayerController, Input, CapsuleCollider, Transform, Camera, MeshCollider
from core.systems import CollisionSystem, TransformSystem, MeshRendererSystem, InputSystem, PlayerControllerSystem, CameraSystem, MeshColliderSystem
from rendering import ShadowMapper, ColliderDebugger
from collisions import SpatialGrid
from ui import UIRenderer, UIText, UIFloat, UIButton
from maths.matrices import get_view_matrix
from rendering.skybox import generate_skybox

engine_start = time.perf_counter()

GL_GPU_MEMORY_INFO_TOTAL_AVAILABLE_MEMORY_NVX = 0x9048
GL_GPU_MEMORY_INFO_CURRENT_AVAILABLE_VIDMEM_NVX = 0x9049

PLAY_MODE = True
PLAY_TEXT = ["[EDITOR]", ""]

WIREFRAME = False

DEBUG_COLLIDERS = False
GRAVITY = -9.81

pygame.init()

screen_width, screen_height = 2560, 1440
screen = pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

light_dir = (1.0, 0.5, 0.0)

ctx = moderngl.create_context()

renderer = Renderer(ctx, screen_width, screen_height)
renderer.build_pipeline(light_dir)

shadow_mapper = ShadowMapper(ctx, tuple(-x for x in light_dir), 4096)

input_manager = InputManager()

transform_system = TransformSystem(None)
mesh_renderer_system = MeshRendererSystem(None, renderer)
mesh_collider_system = MeshColliderSystem(None, renderer)

scene = Scene("Warehouse", renderer, shadow_mapper)
transform_system.em = scene.em
mesh_renderer_system.em = scene.em
mesh_collider_system.em = scene.em

renderer.load_env_map("assets/textures/Day-HDRI.exr")
skybox, skybox_prog = generate_skybox(ctx)

scene.load_scene("main", ctx)

collider_debugger = ColliderDebugger(ctx, scene.em, mesh_collider_system)

collision_system = CollisionSystem(scene.em)
input_system = InputSystem(scene.em)
camera_system = CameraSystem(scene.em, transform_system)

for eid in scene.em.query("Camera"):
    if scene.em.entities[eid].components["Camera"].active:
        cam_eid = eid
        break

cam_t = scene.em.entities[cam_eid].components["Transform"]
cam = scene.em.entities[cam_eid].components["Camera"]

renderer.set_camera(cam_t, cam)

player_controller_system = PlayerControllerSystem(scene.em, cam_t, PLAY_MODE)

for eid in scene.em.query("PlayerController"):
    player_eid = eid

scene.generate_buffers()

grid = SpatialGrid(5.0)
triangles = mesh_collider_system.get_collision_triangles(grid)

process = psutil.Process(os.getpid())
total_ram = psutil.virtual_memory().total

ui_renderer = UIRenderer(ctx, (screen_width, screen_height))
ui_renderer.add_quad(
    UIText(
        0.5,
        0.15,
        "",
        pygame.font.SysFont("consolas", 40),
        ctx,
        (255,255,255),
        "centre"
    )
)

ui_renderer.add_quad(
    UIText(
        0.88,
        0.125,
        "",
        pygame.font.SysFont("consolas", 25),
        ctx,
        (255,255,255),
        "right"
    )
)

ui_renderer.add_quad(
    UIText(
        0.88,
        0.15,
        "",
        pygame.font.SysFont("consolas", 25),
        ctx,
        (255,255,255),
        "right"
    )
)

ui_renderer.add_quad(
    UIText(
        0.88,
        0.175,
        "",
        pygame.font.SysFont("consolas", 25),
        ctx,
        (255,255,255),
        "right"
    )
)

ui_renderer.add_quad(
    UIText(
        0.88,
        0.2,
        "",
        pygame.font.SysFont("consolas", 25),
        ctx,
        (255,255,255),
        "right"
    )
)

ui_renderer.add_quad(
    UIText(
        0.88,
        0.225,
        "",
        pygame.font.SysFont("consolas", 25),
        ctx,
        (255,255,255),
        "right"
    )
)

ui_renderer.add_quad(
    UIText(
        0.88,
        0.25,
        "",
        pygame.font.SysFont("consolas", 25),
        ctx,
        (255,255,255),
        "right"
    )
)

ui_renderer.add_quad(
    UIFloat(
        0.15,
        0.18,
        "Exposure:",
        1.5,
        pygame.font.SysFont("consolas", 25),
        ctx,
        (255,255,255),
        "left"
    )
)

ui_renderer.add_quad(
    UIButton(
        0.15,
        0.205,
        0.1,
        ctx,
        "assets/textures/DefaultButton.png",
        "left"
    )
)

ui_renderer.add_quad(
    UIText(
        0.166,
        0.205,
        "Save Scene",
        pygame.font.SysFont("consolas", 25),
        ctx,
        anchor="left"
    )
)

ui_renderer.add_quad(
    UIButton(
        0.15,
        0.225,
        0.1,
        ctx,
        "assets/textures/DefaultButton.png",
        "left"
    )
)

ui_renderer.add_quad(
    UIText(
        0.166,
        0.225,
        "Load Scene",
        pygame.font.SysFont("consolas", 25),
        ctx,
        anchor="left"
    )
)

render_pipeline = RenderPipeline(ctx, renderer, skybox, skybox_prog, shadow_mapper, collider_debugger, ui_renderer, mesh_renderer_system)

dt=0
dt_real=0
fps=0

total_kb = GL.glGetIntegerv(GL_GPU_MEMORY_INFO_TOTAL_AVAILABLE_MEMORY_NVX)

scene.save_scene("main")

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
    
    ui_renderer.get_quad(0).update_text(PLAY_TEXT[PLAY_MODE])
    ui_renderer.get_quad(1).update_text(f"fps: {fps:.1f}")
    ui_renderer.get_quad(2).update_text(f"fps_raw: {1/dt_real if dt_real > 0 else float('inf'):.1f}")
    ui_renderer.get_quad(3).update_text(f"mem: {process.memory_info().rss / 1048576:.1f}MB")
    
    available_kb = GL.glGetIntegerv(GL_GPU_MEMORY_INFO_CURRENT_AVAILABLE_VIDMEM_NVX)
    used_kb = total_kb - available_kb
    ui_renderer.get_quad(4).update_text(f"vram: {used_kb / 1024:.1f}MB")

    ui_renderer.get_quad(5).update_text(f"dt: {dt*1000:.1f}ms")
    ui_renderer.get_quad(6).update_text(f"dt_raw: {dt_real*1000:.1f}ms")

    exposure_ui = ui_renderer.get_quad(7)
    exposure_ui.update()
    for eid in camera_system.em.query("Camera", "Transform"):
        cam = camera_system.em.entities[eid]
        cam.components["Camera"].exposure = exposure_ui.value

    if ui_renderer.get_quad(8).update():
        scene.save_scene("main")
    
    if ui_renderer.get_quad(10).update():
        scene.load_scene("main", ctx)
        scene.generate_buffers()

        for eid in scene.em.query("Camera"):
            if scene.em.entities[eid].components["Camera"].active:
                cam_eid = eid
                break

        cam_t = scene.em.entities[cam_eid].components["Transform"]
        cam = scene.em.entities[cam_eid].components["Camera"]

        renderer.set_camera(cam_t, cam)

        player_controller_system = PlayerControllerSystem(scene.em, cam_t, PLAY_MODE)

        for eid in scene.em.query("PlayerController"):
            player_eid = eid

        grid = SpatialGrid(5.0)
        triangles = mesh_collider_system.get_collision_triangles(grid)

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
    
    ctx.wireframe = WIREFRAME

    camera_system.update(keys, dt, ui_renderer)

    if PLAY_MODE:
        transform_system.set_pos(player_eid, cam_t.pos)
    
    transform_system.update()
    
    renderer.view = get_view_matrix(cam_t)

    shadow_mapper.update(cam_t)

    render_pipeline.render_frame(scene)

    pygame.display.set_caption(f"Engine | {fps:.0f}fps")

    pygame.display.flip()

    dt_real = time.perf_counter()-start
    dt = clock.tick(60)/1000
    fps = clock.get_fps()