from rendering import RenderEngine
from core import EntityManager
from editor.hierarchy import Hierarchy
from core.logger import Logger
from maths.python import Vec3

NINF = -2_147_483_648
INF = 2_147_483_647

NINF_FLOAT = float("-inf")
INF_FLOAT = float("inf")

class Inspector:
    def __init__(self, render_engine: RenderEngine, entity_manager: EntityManager, hierarchy: Hierarchy):
        self.render_engine = render_engine
        self.entity_manager = entity_manager
        self.hierarchy = hierarchy

        self.cache = {}

    def get_attributes(self, component_type, component):
        if component_type not in self.cache:
            self.cache[component_type] = [
                (
                    name,
                    type(value)
                )
                for name, value in vars(component).items()
                if name != "entity"
            ]

        return self.cache[component_type]

    def update(self, logger: Logger):
        selected_eid = self.hierarchy.selected

        self.render_engine.begin_window("Inspector")

        if selected_eid is not None:
            entity = self.entity_manager.entities[selected_eid]

            for component_type, component_instance in entity.components.items():
                self.render_engine.separator_text(component_type)

                for name, value_type in self.get_attributes(component_type, component_instance):
                    value = getattr(component_instance, name)

                    if value_type == bool:
                        changed, new_value = self.render_engine.checkbox(name, value)

                        if changed:
                            setattr(component_instance, name, new_value)

                    elif value_type == int:
                        changed, new_value = self.render_engine.drag_int(name, value, 1.0, NINF, INF)

                        if changed:
                            setattr(component_instance, name, new_value)

                    elif value_type == float:
                        changed, new_value = self.render_engine.drag_float(name, value, 1.0, NINF_FLOAT, INF_FLOAT)
                        
                        if changed:
                            setattr(component_instance, name, new_value)

                    elif value_type == str:
                        changed, new_value = self.render_engine.input_text(f"{name}##{selected_eid}", value)

                        if changed:
                            setattr(component_instance, name, new_value)

                    elif value_type == Vec3:
                        self.render_engine.drag_float3(name, value, 1.0, NINF_FLOAT, INF_FLOAT)
                    else:
                        logger.log_warning(f"Unsupported type {type(value)} in inspector")

        self.render_engine.end_window()