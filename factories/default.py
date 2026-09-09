import traceback

from shard.maths.python import Vec3
from shard.rendering import PBRMaterial, SkyboxMaterial
from shard.core.components import Name, Transform, MeshRenderer, MeshCollider, LinearBody, CapsuleCollider, Camera, FlyController, DirectionalLight, Script
from shard.collisions import BVH

def build_scene(engine):
    try:
        # Load Scene
        skybox_eid, _ = engine.managers.entity.create_entity()
        engine.managers.entity.add_component(skybox_eid, Name("Skybox", "Skybox"))
        engine.managers.entity.add_component(skybox_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
        engine.managers.entity.add_component(skybox_eid, MeshRenderer())
        engine.systems.mesh_renderer.set_mesh(skybox_eid, "assets/models/Cube.obj")
        engine.systems.mesh_renderer.set_material(skybox_eid, SkyboxMaterial(engine.render_engine, engine.managers.asset, "assets/textures/Sunset-HDRI.exr"))

        light_eid, _ = engine.managers.entity.create_entity()
        engine.managers.entity.add_component(light_eid, Name("Directional Light"))
        engine.managers.entity.add_component(light_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
        engine.managers.entity.add_component(light_eid, DirectionalLight())

        cam_eid, _ = engine.managers.entity.create_entity()
        engine.managers.entity.add_component(cam_eid, Name("Camera", "MainCamera"))
        engine.managers.entity.add_component(cam_eid, Transform(Vec3(0,5,0), Vec3(0,0,0), Vec3(1,1,1)))
        engine.managers.entity.add_component(cam_eid, Camera(True))
        engine.managers.entity.add_component(cam_eid, FlyController())

        plane_eid, _ = engine.managers.entity.create_entity()
        engine.managers.entity.add_component(plane_eid, Name("Plane"))
        engine.managers.entity.add_component(plane_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
        engine.managers.entity.add_component(plane_eid, MeshRenderer())
        engine.managers.entity.add_component(plane_eid, MeshCollider(None))
        engine.systems.mesh_renderer.set_mesh(plane_eid, "assets/models/Quad.obj")
        engine.systems.mesh_renderer.set_material(plane_eid, PBRMaterial(engine.render_engine, engine.managers.asset, engine.logger, "assets/textures/Empty.png", "assets/textures/EmptyNormal.png", "assets/textures/EmptyHeightmap.png", "assets/textures/EmptyORM.png"))
        engine.systems.collision.set_mesh(plane_eid, "assets/models/Quad.obj")


        # Build collision BVH
        engine.bvh = BVH()
        engine.triangles = engine.systems.collision.get_collision_triangles(engine.bvh)
    
    except Exception as e:
        engine.logger.log_fatal(f"Scene loading failed:\n{traceback.format_exc()}")