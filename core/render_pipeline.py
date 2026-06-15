import moderngl

NORMAL_VISUALISER = False

class RenderPipeline:
    def __init__(self, ctx, renderer, skybox, skybox_prog, skybox_settings, shadow_mapper, collider_debugger, ui_renderer, mesh_renderer_system):
        self.ctx = ctx
        self.renderer = renderer
        self.skybox = skybox
        self.skybox_prog = skybox_prog
        self.shadow_mapper = shadow_mapper
        self.collider_debugger = collider_debugger
        self.ui_renderer = ui_renderer
        self.mesh_renderer_system = mesh_renderer_system

        self.skybox_settings = skybox_settings

    def render_frame(self, scene):
        self.ctx.clear(0.05, 0.05, 0.08, 1.0)
        
        self.ctx.disable(moderngl.CULL_FACE)
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.depth_mask = False

        self.skybox_prog['view'].write(self.renderer.view.T.astype("f4").tobytes())
        self.skybox_prog['proj'].write(self.renderer.proj.T.astype("f4").tobytes())

        if self.skybox_settings.procedural:
            self.skybox_prog['sun_dir'].value = tuple(self.skybox_settings.sun_dir)
            self.skybox_prog['sun_color'].value = tuple(self.skybox_settings.sun_col)
        else:
            self.skybox_prog['env_map'] = 3


        self.skybox.render()
        self.ctx.enable(moderngl.CULL_FACE)
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.ctx.depth_mask = True

        self.shadow_mapper.update_light_dir(self.skybox_settings.sun_dir)

        self.shadow_mapper.render_depth(scene)
        self.shadow_mapper.depth_tex.use(location=4)

        if not NORMAL_VISUALISER:
            self.renderer.program["shadow_map"] = 4
            self.renderer.program["light_space"].write(
                self.shadow_mapper.light_space_matrix
                .astype("f4").T.tobytes()
            )

        self.mesh_renderer_system.render(self.renderer.program, self.renderer.proj, self.renderer.env_map, self.renderer.cam_transform, self.renderer.camera, NORMAL_VISUALISER, self.skybox_settings.sun_dir)
        self.collider_debugger.draw(self.renderer)

        self.ui_renderer.render()