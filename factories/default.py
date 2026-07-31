import traceback

from shard.maths.python import Vec3
from shard.rendering import PBRMaterial, SkyboxMaterial
from shard.core.components import Name, Transform, MeshRenderer, MeshCollider, LinearBody, CapsuleCollider, Camera, FlyController
from shard.collisions import BVH

class DefaultScene:
    def __init__(self, skybox_eid: int, player_eid: int, cam_eid: int, warehouse_eid: int, light_dir: Vec3):
        self.skybox_eid = skybox_eid
        self.player_eid = player_eid
        self.cam_eid = cam_eid
        self.warehouse_eid = warehouse_eid
        self.light_dir = light_dir

def build_scene(engine):
    try:
        # Load Scene
        skybox_eid, _ = engine.managers.entity.create_entity()
        engine.managers.entity.add_component(skybox_eid, Name("Skybox", "Skybox"))
        engine.managers.entity.add_component(skybox_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
        engine.managers.entity.add_component(skybox_eid, MeshRenderer())
        engine.systems.mesh_renderer.set_mesh(skybox_eid, "assets/models/Cube.obj")
        engine.systems.mesh_renderer.set_material(skybox_eid, SkyboxMaterial(engine.render_engine, engine.managers.asset, "assets/textures/Day-HDRI.exr"))

        player_eid, _ = engine.managers.entity.create_entity()
        engine.managers.entity.add_component(player_eid, Name("Player"))
        engine.managers.entity.add_component(player_eid, Transform(Vec3(0,10,0), Vec3(0,0,0), Vec3(1,1,1)))
        engine.managers.entity.add_component(player_eid, MeshRenderer())
        engine.managers.entity.add_component(player_eid, LinearBody())
        engine.managers.entity.add_component(player_eid, CapsuleCollider(2, 1, 0))
        engine.systems.mesh_renderer.set_mesh(player_eid, "assets/models/Player.obj")
        engine.systems.mesh_renderer.set_material(player_eid, PBRMaterial(engine.render_engine, engine.managers.asset, engine.logger, "assets/textures/Empty.png", "assets/textures/EmptyNormal.png", "assets/textures/EmptyHeightmap.png", "assets/textures/EmptyORM.png"))

        cam_eid, _ = engine.managers.entity.create_entity()
        engine.managers.entity.add_component(cam_eid, Name("Camera", "MainCamera"))
        engine.managers.entity.add_component(cam_eid, Transform(Vec3(0,5,0), Vec3(0,0,0), Vec3(1,1,1)))
        engine.managers.entity.add_component(cam_eid, Camera(True))
        engine.managers.entity.add_component(cam_eid, FlyController())

        warehouse_eid, _ = engine.managers.entity.create_entity()
        engine.managers.entity.add_component(warehouse_eid, Name("Warehouse"))
        engine.managers.entity.add_component(warehouse_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
        engine.managers.entity.add_component(warehouse_eid, MeshRenderer())
        engine.managers.entity.add_component(warehouse_eid, MeshCollider(None))
        engine.systems.mesh_renderer.set_mesh(warehouse_eid, "assets/models/WarehouseCollider.obj")
        engine.systems.mesh_renderer.set_material(warehouse_eid, PBRMaterial(engine.render_engine, engine.managers.asset, engine.logger, "assets/textures/Empty.png", "assets/textures/EmptyNormal.png", "assets/textures/EmptyHeightmap.png", "assets/textures/EmptyORM.png"))
        engine.systems.collision.set_mesh(warehouse_eid, "assets/models/WarehouseCollider.obj")

        light_dir = Vec3(-0.3, -1.0, -0.2)

        # Build collision BVH
        engine.bvh = BVH()
        engine.triangles = engine.systems.collision.get_collision_triangles(engine.bvh)

        return DefaultScene(skybox_eid, player_eid, cam_eid, warehouse_eid, light_dir)
    
    except Exception as e:
        engine.logger.log_fatal(f"Scene loading failed:\n{traceback.format_exc()}")