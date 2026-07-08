from rendering import RenderEngine, Camera, PlayerController, Mat4, model_matrix, Vec3, PBRMaterial, SkyboxMaterial
from ..entity import EntityManager
from ..asset_manager import AssetManager

class MeshRendererSystem:
    def __init__(self, entity_manager: EntityManager, asset_manager: AssetManager):
        self.entity_manager = entity_manager
        self.asset_manager = asset_manager

    def set_mesh(self, eid, path):
        self.entity_manager.entities[eid].components["MeshRenderer"].mesh_handle = self.asset_manager.get_mesh(path)

    def set_material(self, eid, material):
        self.entity_manager.entities[eid].components["MeshRenderer"].material = material

    def update(self, render_engine, light_dir, cam):
        # Update materials
        for eid in self.entity_manager.query("MeshRenderer", "Transform"):
            entity = self.entity_manager.entities[eid]
            mesh_renderer = entity.components["MeshRenderer"]

            is_skybox = "Skybox" in entity.components

            if is_skybox:
                mesh_renderer.material.update(render_engine, cam)
            else:
                mesh_renderer.material.update(render_engine, cam, light_dir)

        # Shadow Pass
        render_engine.begin_shadows(Vec3(-light_dir.x, -light_dir.y, -light_dir.z), cam.position)
        for eid in self.entity_manager.query("MeshRenderer", "Transform"):
            entity = self.entity_manager.entities[eid]

            if "Skybox" in entity.components:
                continue
            
            transform = entity.components["Transform"]
            mesh_renderer = entity.components["MeshRenderer"]

            render_engine.draw_shadow(mesh_renderer.mesh_handle, transform.model)

        render_engine.end_shadows()

        # Render Pass
        render_engine.begin_frame()

        for eid in self.entity_manager.query("MeshRenderer", "Transform"):
            entity = self.entity_manager.entities[eid]
            transform = entity.components["Transform"]
            mesh_renderer = entity.components["MeshRenderer"]
        
            is_skybox = "Skybox" in entity.components

            if is_skybox:
                render_engine.disable_depth_test()
                render_engine.disable_cull_face()

            render_engine.draw_mesh(mesh_renderer.mesh_handle, mesh_renderer.material.material, transform.model)

            if is_skybox:
                render_engine.enable_depth_test()
                render_engine.enable_cull_face()

        render_engine.end_frame()


