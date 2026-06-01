import pygame
import moderngl
import numpy as np
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
from physics.rigidbody import Rigidbody
from scenes.sponza_scene import SponzaSceneBuilder

DEBUG_COLLIDERS = False
GRAVITY = -9.81

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

scene, skybox, skybox_prog = SponzaSceneBuilder.build(ctx, renderer, shadow_mapper, DEBUG_COLLIDERS)

player = GameObject("Player", Transform.identity(), Material.identity(ctx))
player.load_model("assets/models/Player.obj")
player_capsule = Capsule(0.35, 2.0, -0.8)
player_capsule.position[1] = 5
player_rb = Rigidbody()
speed = 2.5
scene.add(player)

grid = SpatialGrid(1.0)
triangles = scene.get_collision_triangles(grid)

render_pipeline = RenderPipeline(ctx, renderer, skybox, skybox_prog, shadow_mapper, collider_debugger)

dt=0
fps=0

grounded = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    keys = pygame.key.get_pressed()

    camera.process_inputs(keys, dt)   

    move = np.zeros(3)

    if keys[pygame.K_w]:
        move += camera.front * speed * dt
    if keys[pygame.K_s]:
        move -= camera.front * speed * dt
    if keys[pygame.K_a]:
        move -= camera.right * speed * dt
    if keys[pygame.K_d]:
        move += camera.right * speed * dt
    if keys[pygame.K_SPACE] and grounded:
        player_rb.velocity += camera.world_up * 5
    if keys[pygame.K_LSHIFT]:
        move -= camera.world_up * speed * dt

    if keys[pygame.K_LCTRL]:
        speed = 5.0
    else:
        speed = 2.5

    move[1] = 0

    player_capsule.position += move

    if dt < 1:
        player_rb.velocity[1] += GRAVITY * dt

    player_capsule.position += player_rb.velocity * dt

    grounded, normal = solve_capsule(
        player_capsule,
        triangles,
        grid
    )

    if grounded:
        if player_rb.velocity[1] < 0:
            player_rb.velocity[1] = 0

    camera.position = player_capsule.position

    shadow_mapper.update(camera)
    player.set_transform(Transform(camera.position, (0,0,0), (1,1,1)))    

    render_pipeline.render_frame(scene)

    pygame.display.set_caption(f"Engine | {fps:.0f}fps")

    pygame.display.flip()
    dt = clock.tick(60)/1000
    fps = clock.get_fps()