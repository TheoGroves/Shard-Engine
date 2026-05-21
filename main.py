import pygame
import moderngl
from core.camera import Camera
from core.renderer import Renderer
from core.material import Material
from core.game_object import GameObject
from core.transform import Transform
from core.scene import Scene

pygame.init()

screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

camera = Camera((0, 0, 5))

ctx = moderngl.create_context()
renderer = Renderer(ctx, screen_width, screen_height, camera)
renderer.build_pipeline()

scene = Scene("Main")

bunny = GameObject("Bunny", Transform((0, 0, 0), (0,0,0)), Material(ctx, "assets/textures/ClayDiffuse.jpg", "assets/textures/ClayNormal.jpg", 16.0))
bunny.load_model("assets/models/StanfordBunny.obj")

suzanne = GameObject("Suzanne", Transform((2, 0.5, 0), (0,0,0)), Material(ctx, "assets/textures/PlasterDiffuse.jpg", "assets/textures/PlasterNormal.jpg", 64.0))
suzanne.load_model("assets/models/Suzanne.obj")

renderer.load_mesh(bunny)
renderer.load_mesh(suzanne)

scene.add(bunny)
scene.add(suzanne)

dt=0
fps=0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    camera.process_inputs(pygame.key.get_pressed(), dt)   
    
    renderer.render(scene)

    pygame.display.set_caption(f"Engine | {fps:.0f}fps")

    pygame.display.flip()
    dt = clock.tick(60)/1000
    fps = clock.get_fps()