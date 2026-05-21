import pygame
import moderngl
from camera import Camera
from renderer import Renderer
from obj_parser import parse_objs, build_interleaved

pygame.init()

vertex_buffer, normal_buffer, tangent_buffer, bitangent_buffer, uv_buffer, index_buffer, normal_index_buffer, uv_index_buffer = parse_objs(["models/StanfordBunny.obj"])

vertices_np, indices_np = build_interleaved(
    vertex_buffer,
    normal_buffer,
    tangent_buffer,
    bitangent_buffer,
    uv_buffer,
    index_buffer,
    normal_index_buffer,
    uv_index_buffer
)

screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

camera = Camera((0, 0, 5))

ctx = moderngl.create_context()
renderer = Renderer(ctx, screen_width, screen_height, camera)

renderer.load_mesh(vertices_np, indices_np)
renderer.build_pipeline()

dt=0
fps=0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    camera.process_inputs(pygame.key.get_pressed(), dt)   
    
    renderer.render()

    pygame.display.set_caption(f"Engine | {fps:.0f}fps")

    pygame.display.flip()
    dt = clock.tick(60)/1000
    fps = 1/dt