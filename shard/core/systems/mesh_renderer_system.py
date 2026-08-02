from shard_maths import Mat4, model_matrix, Vec3, round_to
from shard.rendering import RenderEngine, Camera, PlayerController, PBRMaterial, SkyboxMaterial
from ..entity import EntityManager
from ..asset_manager import AssetManager

class MeshRendererSystem:
    def __init__(self, entity_manager: EntityManager, asset_manager: AssetManager, logger):
        self.entity_manager = entity_manager
        self.asset_manager = asset_manager
        self.logger = logger

    def set_mesh(self, eid, path):
        self.entity_manager.entities[eid].components["MeshRenderer"].mesh_handle, _ = self.asset_manager.get_mesh(path)

    def set_material(self, eid, material):
        self.entity_manager.entities[eid].components["MeshRenderer"].material = material

    def update(self, render_engine, cam, viewport):
        # Get light direction from directional light
        light_dir = Vec3(0,0,0)
        for eid in self.entity_manager.query("DirectionalLight"):
            light_dir = self.entity_manager.entities[eid].components["DirectionalLight"].light_dir

        # Shadow Pass
        render_engine.begin_shadows(Vec3(-light_dir.x, -light_dir.y, -light_dir.z), Vec3(0,0,0))
        for eid in self.entity_manager.query("MeshRenderer", "Transform"):
            entity = self.entity_manager.entities[eid]

            if entity.components["Name"].tag == "Skybox":
                continue
            
            transform = entity.components["Transform"]
            mesh_renderer = entity.components["MeshRenderer"]

            if mesh_renderer.mesh_handle:
                render_engine.draw_shadow(mesh_renderer.mesh_handle, transform.world)

        render_engine.end_shadows()

        # Fetch Env Map from skybox
        env = None

        for eid in self.entity_manager.query("MeshRenderer", "Name"):
            entity = self.entity_manager.entities[eid]
            mesh_renderer = entity.components["MeshRenderer"]
            name = entity.components["Name"]
            if name.tag == "Skybox":
                if env is not None:
                    self.logger.log_warning("Multiple skyboxes found. Only one skybox can be used for IBL. Use only one skybox.")
                env = mesh_renderer.material.env
                irr = mesh_renderer.material.irr

        # Render Pass
        render_engine.begin_frame()

        viewport.bind()

        for eid in self.entity_manager.query("MeshRenderer", "Transform"):
            entity = self.entity_manager.entities[eid]
            transform = entity.components["Transform"]
            mesh_renderer = entity.components["MeshRenderer"]
        
            is_skybox = entity.components["Name"].tag == "Skybox"

            if mesh_renderer.material is not None:
                if is_skybox:
                    mesh_renderer.material.update(render_engine, cam, light_dir)
                else:
                    if irr is not None and env is not None:
                        mesh_renderer.material.update(render_engine, cam, light_dir, env, irr)

            if is_skybox:
                render_engine.disable_depth_test()
                render_engine.disable_cull_face()

            if mesh_renderer.mesh_handle and mesh_renderer.material:
                if is_skybox and mesh_renderer.material.use_procedural: # Switch to procedural material for rendering if selected
                    render_engine.draw_mesh(mesh_renderer.mesh_handle, mesh_renderer.material.proc_material, transform.world)
                else:
                    render_engine.draw_mesh(mesh_renderer.mesh_handle, mesh_renderer.material.material, transform.world)

            if is_skybox:
                render_engine.enable_depth_test()
                render_engine.enable_cull_face()

        viewport.unbind(render_engine.get_width(), render_engine.get_height())
