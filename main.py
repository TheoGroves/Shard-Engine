import pygame
import moderngl
from core.camera import Camera
from core.renderer import Renderer
from core.material import Material
from core.game_object import GameObject
from core.transform import Transform
from core.scene import Scene
from rendering.skybox import generate_skybox

pygame.init()

screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

camera = Camera((0, 0, 5))

ctx = moderngl.create_context()
renderer = Renderer(ctx, screen_width, screen_height, camera)
renderer.build_pipeline()

scene = Scene("Main")

bunny = GameObject("Bunny", Transform((0, 0, 0), (0,90,0)), Material(ctx, "ClayDiffuse.jpg", "ClayNormal.jpg", "ClayHeightmap.jpg", 0.01, 16.0, 1))
bunny.load_model("assets/models/StanfordBunny.obj")

suzanne = GameObject("Suzanne", Transform((0, 0.6, 2), (-10,80,0)), Material(ctx, "PlasterDiffuse.jpg", "PlasterNormal.jpg", "PlasterHeightmap.png", 0.01, 64.0, 1))
suzanne.load_model("assets/models/Suzanne.obj")

floor = GameObject("Floor", Transform((0,0,1), (0,0,0)), Material(ctx, None, None, None, 0, 256, 8))
floor.load_model("assets/models/Plane.obj")

renderer.generate_buffers(bunny)
renderer.generate_buffers(suzanne)
renderer.generate_buffers(floor)

scene.add(bunny)
scene.add(suzanne)
scene.add(floor)

renderer.load_env_map("assets/textures/Day-HDRI.exr")
skybox, skybox_prog = generate_skybox(ctx)

dt=0
fps=0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    camera.process_inputs(pygame.key.get_pressed(), dt)   

    ctx.clear(0.05, 0.05, 0.08, 1.0)
    
    ctx.disable(moderngl.CULL_FACE)
    ctx.disable(moderngl.DEPTH_TEST)
    ctx.depth_mask = False

    skybox_prog['env_map'] = 3
    skybox_prog['view'].write(renderer.view.T.astype("f4").tobytes())
    skybox_prog['proj'].write(renderer.proj.T.astype("f4").tobytes())
    skybox.render()
    ctx.enable(moderngl.CULL_FACE)
    ctx.enable(moderngl.DEPTH_TEST)

    ctx.depth_mask = True

    renderer.render(scene)

    pygame.display.set_caption(f"Engine | {fps:.0f}fps")

    pygame.display.flip()
    dt = clock.tick(60)/1000
    fps = clock.get_fps()