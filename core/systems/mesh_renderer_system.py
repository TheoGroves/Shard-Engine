from ecs import EntityManager
from loaders.obj_parser import parse_objs, build_interleaved
from core.mesh import Mesh
from core.renderer import Renderer
from maths.matrices import get_view_matrix
from core.asset_manager import AssetManager

class MeshRendererSystem:
    def __init__(self, em: EntityManager, renderer: Renderer, asset_manager: AssetManager):
        self.em = em
        self.renderer = renderer
        self.asset_manager = asset_manager

    def load_model(self, eid, path, shadow_mapper=None):
        mesh_renderer = self.em.entities[eid].components["MeshRenderer"]

        mesh_renderer.mesh = self.asset_manager.get_mesh(path)

        self.renderer.generate_buffers(mesh_renderer)
        
        if shadow_mapper:
            shadow_mapper.generate_shadow_vao(mesh_renderer)

    def set_material(self, eid, material):
        self.em.entities[eid].components["MeshRenderer"].material = material

    def render(self, program, proj, env_map, camera_t, camera, NORMAL_VISUALISER, light_dir):
        view = get_view_matrix(camera_t)

        program["view"].write(view.astype("f4").T.tobytes())
        program["proj"].write(proj.astype("f4").T.tobytes())

        if not NORMAL_VISUALISER:
            program["light_dir"].value = light_dir
            program["cam_pos"].value = tuple(camera_t.pos)
            program["tonemapExposure"] = camera.exposure

        for eid in self.em.query("Transform", "MeshRenderer"):
            entity = self.em.entities[eid]
            transform = entity.components["Transform"]
            mesh_renderer = entity.components["MeshRenderer"]

            program["model"].write(transform.model.astype("f4").T.tobytes())
            program["uv_scale"].value = mesh_renderer.material.uv_scale
            
            if mesh_renderer.material.texture:
                mesh_renderer.material.texture.use(location=0)
                program["tex"] = 0

            if mesh_renderer.material.normal_map:
                mesh_renderer.material.normal_map.use(location=1)
                program["normal_map"] = 1

            if not NORMAL_VISUALISER:
                if mesh_renderer.material.heightmap:
                    mesh_renderer.material.heightmap.use(location=2)
                    program["height_map"] = 2
                    program["height_scale"].value = mesh_renderer.material.height_scale

                if env_map:
                    env_map.use(location=3)
                    program["env_map"] = 3

                if mesh_renderer.material.orm_map:
                    mesh_renderer.material.orm_map.use(location=5)
                    program["orm_map"] = 5

            mesh_renderer.mesh.vao.render()