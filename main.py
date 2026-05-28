import pygame
import moderngl
from core.camera import Camera
from core.renderer import Renderer
from core.material import Material
from core.game_object import GameObject
from core.transform import Transform
from core.scene import Scene
from rendering.skybox import generate_skybox
from rendering.shadow_mapper import ShadowMapper
from importers.asset_importer import load_many

pygame.init()

screen_width, screen_height = 2560, 1440
screen = pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

camera = Camera((0, 0, 5))

light_dir = (0.7, 1.5, 0.2)

ctx = moderngl.create_context()
renderer = Renderer(ctx, screen_width, screen_height, camera)
renderer.build_pipeline(light_dir)

loaded_objects = load_many(ctx, renderer, "assets/models/SponzaModels", "assets/textures/SponzaTextures")

shadow_mapper = ShadowMapper(ctx, tuple(-x for x in light_dir), 4096)

scene = Scene("Main", shadow_mapper)

for go in loaded_objects.values():
    scene.add(go)

player = GameObject("Player", Transform((0, 0, 0), (0,90,0)), Material(ctx, None, None, None, 0, 32.0, 1))
player.load_model("assets/models/Player.obj")
renderer.generate_buffers(player)
scene.add(player)

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
    player.set_transform(Transform(camera.position, (0,0,0)))

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

    shadow_mapper.render_depth(scene)
    shadow_mapper.depth_tex.use(location=4)
    renderer.program["shadow_map"] = 4
    renderer.program["light_space"].write(
        shadow_mapper.light_space_matrix
        .astype("f4").T.tobytes()
    )

    renderer.render(scene)

    pygame.display.set_caption(f"Engine | {fps:.0f}fps")

    pygame.display.flip()
    dt = clock.tick(60)/1000
    fps = clock.get_fps()