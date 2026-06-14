import pygame
import moderngl
from OpenGL import GL
import os
import psutil
import time

from core import Renderer, Material, RenderPipeline, InputManager, Mesh
from core.components import MeshRenderer, Rigidbody, PlayerController, Input, CapsuleCollider, Transform, Camera
from core.systems import CollisionSystem, TransformSystem, MeshRendererSystem, InputSystem, PlayerControllerSystem, CameraSystem, MeshColliderSystem
from rendering import ShadowMapper, ColliderDebugger
from collisions import SpatialGrid
from scenes import WarehouseSceneBuilder
from ui import UIRenderer, UIText, UIFloat
from maths.matrices import get_view_matrix

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

scene, skybox, skybox_prog = WarehouseSceneBuilder.build(ctx, renderer, shadow_mapper, DEBUG_COLLIDERS, transform_system, mesh_renderer_system, mesh_collider_system)

collider_debugger = ColliderDebugger(ctx, scene.em, mesh_collider_system)

collision_system = CollisionSystem(scene.em)
input_system = InputSystem(scene.em)
camera_system = CameraSystem(scene.em, transform_system)

cam_eid = scene.em.create_entity()
scene.em.add_component(cam_eid, Transform())
scene.em.add_component(cam_eid, Camera(screen_width, screen_height))

cam_t = scene.em.entities[cam_eid].components["Transform"]
cam = scene.em.entities[cam_eid].components["Camera"]

renderer.set_camera(cam_t, cam)

player_controller_system = PlayerControllerSystem(scene.em, cam_t, PLAY_MODE)

player_eid = scene.em.create_entity()
scene.em.add_component(player_eid, Transform.identity())
scene.em.add_component(player_eid, MeshRenderer(Mesh(), None, Material.identity(ctx)))
scene.em.add_component(player_eid, CapsuleCollider(0.35, 1.6, -0.8))
scene.em.add_component(player_eid, Rigidbody())
scene.em.add_component(player_eid, PlayerController())
scene.em.add_component(player_eid, Input())

transform_system.set_pos(player_eid, (0, 5, 0))
transform_system.set_scale(player_eid, (1,1.45,1))
mesh_renderer_system.load_model(player_eid, "assets/models/Player.obj", shadow_mapper)

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

render_pipeline = RenderPipeline(ctx, renderer, skybox, skybox_prog, shadow_mapper, collider_debugger, ui_renderer, mesh_renderer_system)

dt=0
dt_real=0
fps=0

total_kb = GL.glGetIntegerv(GL_GPU_MEMORY_INFO_TOTAL_AVAILABLE_MEMORY_NVX)

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

    ram_use = process.memory_info().rss/total_ram
    if ram_use > 0.5:
        print(f"WARNING: {ram_use * 100:.1f}% of RAM used")

    if input_manager.is_key_just_pressed(pygame.K_c):
        PLAY_MODE = not PLAY_MODE
        player_controller_system.play_mode = PLAY_MODE

    if input_manager.is_key_just_pressed(pygame.K_x):
        WIREFRAME = not WIREFRAME

    if input_manager.is_key_just_pressed(pygame.K_g):
        DEBUG_COLLIDERS = not DEBUG_COLLIDERS
        for c in scene.colliders:
            c.debug = DEBUG_COLLIDERS
    
    if PLAY_MODE:
        WIREFRAME = False

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