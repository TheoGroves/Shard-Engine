import pygame
import moderngl
import os
import psutil

from core import Camera, Renderer, Material, GameObject, Transform, RenderPipeline, InputManager
from rendering import ShadowMapper, ColliderDebugger
from collisions import Capsule, SpatialGrid
from physics import Rigidbody
from scenes import WarehouseSceneBuilder
from gameplay import PlayerController
from ui import UIRenderer, UIText

PLAY_MODE = True
PLAY_TEXT = ["[EDITOR]", ""]

WIREFRAME = False

DEBUG_COLLIDERS = False
GRAVITY = -9.81

pygame.init()

screen_width, screen_height = 2560, 1440
screen = pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

camera = Camera((0, 2, 0))

light_dir = (1.0, 0.5, 0.0)

ctx = moderngl.create_context()
renderer = Renderer(ctx, screen_width, screen_height, camera)
renderer.build_pipeline(light_dir)

shadow_mapper = ShadowMapper(ctx, tuple(-x for x in light_dir), 4096)

collider_debugger = ColliderDebugger(ctx)

input_manager = InputManager()

scene, skybox, skybox_prog = WarehouseSceneBuilder.build(ctx, renderer, shadow_mapper, DEBUG_COLLIDERS)

player = GameObject("Player", Transform(scale=(1,1.45,1)), Material.identity(ctx))
player.load_model("assets/models/Player.obj")
player_capsule = Capsule(0.35, 1.6, -0.8)
player_capsule.position[1] = 5
player_rb = Rigidbody()
player_controller = PlayerController(camera, player_rb, player_capsule)
scene.add(player)

grid = SpatialGrid(5.0)
triangles = scene.get_collision_triangles(grid)

process = psutil.Process(os.getpid())
total_ram = psutil.virtual_memory().total

ui_renderer = UIRenderer(ctx, (screen_width, screen_height))
ui_renderer.add_quad(
    UIText(
        0.5,
        0.15,
        "",
        pygame.font.SysFont("arial", 40),
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
        pygame.font.SysFont("arial", 25),
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
        pygame.font.SysFont("arial", 25),
        ctx,
        (255,255,255),
        "right"
    )
)

render_pipeline = RenderPipeline(ctx, renderer, skybox, skybox_prog, shadow_mapper, collider_debugger, ui_renderer)

dt=0
fps=0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    input_manager.update()
    keys = input_manager.current_keys

    ui_renderer.get_quad(0).update_text(PLAY_TEXT[PLAY_MODE])
    ui_renderer.get_quad(1).update_text(f"FPS: {fps:.1f}")
    ui_renderer.get_quad(2).update_text(f"Memory Usage: {process.memory_info().rss / 1048576:.1f}MB")

    ram_use = process.memory_info().rss/total_ram
    if ram_use > 0.5:
        print(f"WARNING: {ram_use * 100:.1f}% of RAM used")

    if input_manager.is_key_just_pressed(pygame.K_c):
        PLAY_MODE = not PLAY_MODE

    if input_manager.is_key_just_pressed(pygame.K_x):
        WIREFRAME = not WIREFRAME

    if input_manager.is_key_just_pressed(pygame.K_g):
        DEBUG_COLLIDERS = not DEBUG_COLLIDERS
        for c in scene.colliders:
            c.debug = DEBUG_COLLIDERS
    
    if PLAY_MODE:
        WIREFRAME = False

    ctx.wireframe = WIREFRAME

    camera.process_inputs(keys, dt)   

    player_controller.update(keys, dt, triangles, grid, GRAVITY, PLAY_MODE)

    shadow_mapper.update(camera)

    if PLAY_MODE:
        t = player.get_transform()
        t.set_pos(camera.position)
        player.set_transform(t)    

    render_pipeline.render_frame(scene)

    pygame.display.set_caption(f"Engine | {fps:.0f}fps")

    pygame.display.flip()
    dt = clock.tick(60)/1000
    fps = clock.get_fps()