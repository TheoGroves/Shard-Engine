import os

from shard.rendering import RenderEngine, PBRMaterial
from shard.rendering.materials import Material
from shard.core import EntityManager
from editor.hierarchy import Hierarchy
from shard.core.logger import Logger
from shard.maths.python import Vec3
from shard.core.component import COMPONENT_REGISTRY
from shard.core.asset_manager import AssetManager

NINF = -2_147_483_648
INF = 2_147_483_647

NINF_FLOAT = float("-inf")
INF_FLOAT = float("inf")

class Inspector:
    def __init__(self, render_engine: RenderEngine, entity_manager: EntityManager, hierarchy: Hierarchy, asset_manager: AssetManager):
        self.render_engine = render_engine
        self.entity_manager = entity_manager
        self.hierarchy = hierarchy
        self.asset_manager = asset_manager

        self.cache = {}

        self.texture_to_edit = None
        self.mesh_to_edit = None

    def get_attributes(self, component_type, component):
        if component_type not in self.cache:
            inspect_fields = getattr(component, "__inspect__", None)

            if inspect_fields is not None:
                self.cache[component_type] = inspect_fields
            else:
                self.cache[component_type] = {
                    name: None
                    for name in vars(component)
                    if name != "entity"
                }

        return self.cache[component_type]

    def edit_float(self, name, obj, speed=0.1, min_value=NINF_FLOAT, max_value=INF_FLOAT):
        value = getattr(obj, name.split("##")[0])

        changed, new_value = self.render_engine.drag_float(name, value, speed, min_value, max_value)

        if changed:
            setattr(obj, name.split("##")[0], new_value)

    def edit_texture(self, name, obj):
        self.render_engine.text(name)

        value = getattr(obj, name)

        clicked = self.render_engine.image_button(name, value, 32, 32)

        if self.render_engine.is_item_hovered():
            self.render_engine.begin_tooltip()

            img_path = self.asset_manager.texture_paths[value]
            img_name = os.path.basename(img_path)

            self.render_engine.text(img_name)
            self.render_engine.image(value, 128, 128)

            self.render_engine.end_tooltip()
        if clicked:
            self.texture_to_edit = (obj, name)
            self.render_engine.open_popup("edit_texture")

    def edit_texture_env(self, name, obj):
        self.render_engine.text(name)

        value = getattr(obj, name)

        clicked = self.render_engine.image_button(name, value, 32, 32)

        if self.render_engine.is_item_hovered():
            self.render_engine.begin_tooltip()

            env_path = self.asset_manager.env_paths[value]
            env_name = os.path.basename(env_path)

            self.render_engine.text(env_name)
            self.render_engine.image(value, 128, 128)

            self.render_engine.end_tooltip()
        if clicked:
            self.texture_to_edit = (obj, name)
            self.render_engine.open_popup("edit_texture_env")

    def edit_mesh(self, name, obj):
        self.render_engine.text(name)

        handle = getattr(obj, name)

        if handle is not None:
            mesh_path = self.asset_manager.mesh_paths[handle]
            mesh_name = os.path.basename(mesh_path)

        else:
            mesh_name = "None"

        clicked = self.render_engine.button(mesh_name, 0, 0)

        if self.render_engine.is_item_hovered():
            self.render_engine.begin_tooltip()

            mesh_path = self.asset_manager.mesh_paths[handle]
            mesh_name = os.path.basename(mesh_path)

            self.render_engine.text(mesh_name)

            self.render_engine.end_tooltip()
        if clicked:
            self.mesh_to_edit = (obj, name)
            self.render_engine.open_popup("edit_mesh")

    def draw_property(self, obj, name, field_type, logger, selected_eid):
        value = getattr(obj, name)

        if field_type == "bool":
            changed, new_value = self.render_engine.checkbox(f"{name}##{id(obj)}", value)

            if changed:
                setattr(obj, name, new_value)

        elif field_type == "int":
            changed, new_value = self.render_engine.drag_int(f"{name}##{id(obj)}", value, 1.0, NINF, INF)

            if changed:
                setattr(obj, name, new_value)

        elif field_type == "float":
            changed, new_value = self.render_engine.drag_float(f"{name}##{id(obj)}", value, 1.0, NINF_FLOAT, INF_FLOAT)
            
            if changed:
                setattr(obj, name, new_value)

        elif field_type == "string":
            changed, new_value = self.render_engine.input_text(f"{name}##{selected_eid}", value)

            if changed:
                setattr(obj, name, new_value)

        elif field_type == "Vec3":
            self.render_engine.drag_float3(f"{name}##{id(obj)}", value, 1.0, NINF_FLOAT, INF_FLOAT)

        elif field_type == "material":
            if value is not None:
                value.draw_inspector(self)
            else:
                setattr(obj, name, PBRMaterial(self.render_engine, self.asset_manager, logger, "assets/textures/Empty.png", "assets/textures/EmptyNormal.png", "assets/textures/EmptyHeightmap.png", "assets/textures/EmptyORM.png"))

        elif field_type == "mesh":
            self.edit_mesh(name, obj)

        else:
            logger.log_warning(f"Unsupported field {name} type {field_type} in inspector")

    def update(self, logger: Logger):
        selected_eid = self.hierarchy.selected

        self.render_engine.begin_window("Inspector")

        if selected_eid is not None:
            entity = self.entity_manager.entities[selected_eid]

            for component_type, component_instance in entity.components.items():
                self.render_engine.separator_text(component_type)

                for field, field_type in self.get_attributes(component_type, component_instance).items():
                    self.draw_property(component_instance, field, field_type, logger, selected_eid)

            self.render_engine.separator()
            if self.render_engine.button("Add Component", -1, 0):
                self.render_engine.open_popup("component_selector")

            if self.render_engine.begin_popup("component_selector"):
                for comp_name in COMPONENT_REGISTRY:
                    if self.render_engine.menu_item(comp_name):
                        component_class = COMPONENT_REGISTRY[comp_name]
                        self.entity_manager.add_component(self.hierarchy.selected, component_class())

                self.render_engine.end_popup()

            if self.render_engine.begin_popup("edit_texture"):
                obj, name = self.texture_to_edit

                columns = 4
                count = 0

                for texture_id, path in self.asset_manager.texture_paths.items():
                    filename = os.path.basename(path)

                    if self.render_engine.image_button(filename, texture_id, 64, 64):
                        setattr(obj, name, texture_id)

                    count += 1

                    if count % columns != 0:
                        self.render_engine.same_line()

                self.render_engine.end_popup()

            if self.render_engine.begin_popup("edit_texture_env"):
                obj, name = self.texture_to_edit

                columns = 4
                count = 0

                for env_id, path in self.asset_manager.env_paths.items():
                    filename = os.path.basename(path)

                    if self.render_engine.image_button(filename, env_id, 64, 64):
                        setattr(obj, name, env_id)
                        setattr(obj, "irr", self.asset_manager.env_irr_map[env_id])

                    count += 1

                    if count % columns != 0:
                        self.render_engine.same_line()

                self.render_engine.end_popup()

            if self.render_engine.begin_popup("edit_mesh"):
                obj, name = self.mesh_to_edit

                for mesh_handle, path in self.asset_manager.mesh_paths.items():
                    filename = os.path.basename(path)

                    if self.render_engine.button(filename, 0, 0):
                        setattr(obj, name, mesh_handle)

                self.render_engine.end_popup()

        self.render_engine.end_window()