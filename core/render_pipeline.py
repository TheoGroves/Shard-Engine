import moderngl

class RenderPipeline:
    def __init__(self, ctx, renderer, skybox, skybox_prog, shadow_mapper, collider_debugger):
        self.ctx = ctx
        self.renderer = renderer
        self.skybox = skybox
        self.skybox_prog = skybox_prog
        self.shadow_mapper = shadow_mapper
        self.collider_debugger = collider_debugger

    def render_frame(self, scene):
        self.ctx.clear(0.05, 0.05, 0.08, 1.0)
        
        self.ctx.disable(moderngl.CULL_FACE)
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.depth_mask = False

        self.skybox_prog['env_map'] = 3
        self.skybox_prog['view'].write(self.renderer.view.T.astype("f4").tobytes())
        self.skybox_prog['proj'].write(self.renderer.proj.T.astype("f4").tobytes())
        self.skybox.render()
        self.ctx.enable(moderngl.CULL_FACE)
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.ctx.depth_mask = True

        self.shadow_mapper.render_depth(scene)
        self.shadow_mapper.depth_tex.use(location=4)
        self.renderer.program["shadow_map"] = 4
        self.renderer.program["light_space"].write(
            self.shadow_mapper.light_space_matrix
            .astype("f4").T.tobytes()
        )

        self.renderer.render(scene)
        self.collider_debugger.draw(self.renderer, scene.colliders)