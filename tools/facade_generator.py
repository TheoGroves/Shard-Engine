import re

to_edit = """
    try:
        # Load Scene
        skybox_eid, _ = engine.entity_manager.create_entity()
        engine.entity_manager.add_component(skybox_eid, Name("Skybox", "Skybox"))
        engine.entity_manager.add_component(skybox_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
        engine.entity_manager.add_component(skybox_eid, MeshRenderer())
        engine.mesh_renderer_system.set_mesh(skybox_eid, "assets/models/Cube.obj")
        engine.mesh_renderer_system.set_material(skybox_eid, SkyboxMaterial(engine.render_engine, engine.asset_manager, "assets/textures/Day-HDRI.exr"))

        player_eid, _ = engine.entity_manager.create_entity()
        engine.entity_manager.add_component(player_eid, Name("Player"))
        engine.entity_manager.add_component(player_eid, Transform(Vec3(0,10,0), Vec3(0,0,0), Vec3(1,1,1)))
        engine.entity_manager.add_component(player_eid, MeshRenderer())
        engine.entity_manager.add_component(player_eid, LinearBody())
        engine.entity_manager.add_component(player_eid, CapsuleCollider(2, 1, 0))
        engine.mesh_renderer_system.set_mesh(player_eid, "assets/models/Player.obj")
        engine.mesh_renderer_system.set_material(player_eid, PBRMaterial(engine.render_engine, engine.asset_manager, engine.logger, "assets/textures/Empty.png", "assets/textures/EmptyNormal.png", "assets/textures/EmptyHeightmap.png", "assets/textures/EmptyORM.png"))

        cam_eid, _ = engine.entity_manager.create_entity()
        engine.entity_manager.add_component(cam_eid, Name("Camera", "MainCamera"))
        engine.entity_manager.add_component(cam_eid, Transform(Vec3(0,5,0), Vec3(0,0,0), Vec3(1,1,1)))
        engine.entity_manager.add_component(cam_eid, Camera(True))
        engine.entity_manager.add_component(cam_eid, FlyController())

        warehouse_eid, _ = engine.entity_manager.create_entity()
        engine.entity_manager.add_component(warehouse_eid, Name("Warehouse"))
        engine.entity_manager.add_component(warehouse_eid, Transform(Vec3(0,0,0), Vec3(0,0,0), Vec3(1,1,1)))
        engine.entity_manager.add_component(warehouse_eid, MeshRenderer())
        engine.entity_manager.add_component(warehouse_eid, MeshCollider(None))
        engine.mesh_renderer_system.set_mesh(warehouse_eid, "assets/models/WarehouseCollider.obj")
        engine.mesh_renderer_system.set_material(warehouse_eid, PBRMaterial(engine.render_engine, engine.asset_manager, engine.logger, "assets/textures/Empty.png", "assets/textures/EmptyNormal.png", "assets/textures/EmptyHeightmap.png", "assets/textures/EmptyORM.png"))
        engine.collision_system.set_mesh(warehouse_eid, "assets/models/WarehouseCollider.obj")

        light_dir = Vec3(-0.3, -1.0, -0.2)

        # Build collision BVH
        bvh = BVH()
        triangles = engine.collision_system.get_collision_triangles(bvh)
    except Exception as e:
        engine.logger.log_fatal(f"Scene loading failed:\n{traceback.format_exc()}")
"""

wrapper_name = input("Enter name of facade> ")

variables = []
consts = {}

for line in to_edit.splitlines():
    line = line.strip()

    if "=" not in line:
        continue

    var, value = map(str.strip, line.split("=", 1))

    if re.match(r"[A-Z][A-Z0-9_]*$", var):
        consts[var] = value
    else:
        if var not in variables:
            variables.append(var)


class_name = wrapper_name.title().replace(" ", "")

print(f"class {class_name}:")

init_params = ", ".join(["self", *variables])
print(f"    def __init__({init_params}):")

print("        # Constants")
for const, value in consts.items():
    print(f"        self.{const} = {value}")

print("\n        # Variables")
for var in variables:
    print(f"        self.{var} = {var}")

print()
print(f"{wrapper_name.lower()} = {class_name}({', '.join(variables)})")