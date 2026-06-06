import pygame
import moderngl
import numpy as np
from core.camera import Camera
from core.renderer import Renderer
from core.material import Material
from core.game_object import GameObject
from core.transform import Transform
from core.render_pipeline import RenderPipeline
from core.input_manager import InputManager
from rendering.shadow_mapper import ShadowMapper
from rendering.debug_renderer import ColliderDebugger
from collisions.capsule import Capsule
from collisions.spatial_grid import SpatialGrid
from physics.rigidbody import Rigidbody
from scenes.warehouse_scene import WarehouseSceneBuilder
from gameplay.player_controller import PlayerController
from ui.ui_renderer import UIRenderer
from ui.ui_elements import UIText

PLAY_MODE = True
PLAY_TEXT = ["[EDITOR]", "[PLAY]"]

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

ui_renderer = UIRenderer(ctx, (screen_width, screen_height))
ui_renderer.add_quad(
    UIText(
        1280,
        200,
        "",
        pygame.font.SysFont("arial", 36),
        ctx
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

    ui_renderer.quads = []
    ui_renderer.add_quad(
        UIText(
            1280,
            200,
            PLAY_TEXT[PLAY_MODE],
            pygame.font.SysFont("arial", 25),
            ctx
        )
    )

    if input_manager.is_key_just_pressed(pygame.K_c):
        PLAY_MODE = not PLAY_MODE

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