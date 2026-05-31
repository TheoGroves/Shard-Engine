import pygame
import moderngl
from core.camera import Camera
from core.renderer import Renderer
from core.material import Material
from core.game_object import GameObject
from core.transform import Transform
from core.render_pipeline import RenderPipeline
from rendering.shadow_mapper import ShadowMapper
from rendering.debug_renderer import ColliderDebugger
from collisions.capsule import Capsule
from collisions.spatial_grid import SpatialGrid
from collisions.collision_solver import solve_capsule
from scenes.sponza_scene import SponzaSceneBuilder

pygame.init()

screen_width, screen_height = 2560, 1440
screen = pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

camera = Camera((0, 2, 0))

light_dir = (0.3, 1.0, 0.2)

ctx = moderngl.create_context()
renderer = Renderer(ctx, screen_width, screen_height, camera)
renderer.build_pipeline(light_dir)

shadow_mapper = ShadowMapper(ctx, tuple(-x for x in light_dir), 4096)

collider_debugger = ColliderDebugger(ctx)
DEBUG_COLLIDERS = False

scene, skybox, skybox_prog = SponzaSceneBuilder.build(ctx, renderer, shadow_mapper, DEBUG_COLLIDERS)

player = GameObject("Player", Transform.identity(), Material.identity(ctx))
player.load_model("assets/models/Player.obj")
player_capsule = Capsule(0.35, 2.0, -0.8)
scene.add(player)

grid = SpatialGrid(1.0)
triangles = scene.get_collision_triangles(grid)

render_pipeline = RenderPipeline(ctx, renderer, skybox, skybox_prog, shadow_mapper, collider_debugger)

dt=0
fps=0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    camera.process_inputs(pygame.key.get_pressed(), dt)   
    player_capsule.position = camera.position
    shadow_mapper.update(camera)

    solve_capsule(player_capsule, triangles, grid)

    camera.position = player_capsule.position
    player.set_transform(Transform(camera.position, (0,0,0), (1,1,1)))    

    render_pipeline.render_frame(scene)

    pygame.display.set_caption(f"Engine | {fps:.0f}fps")

    pygame.display.flip()
    dt = clock.tick(60)/1000
    fps = clock.get_fps()