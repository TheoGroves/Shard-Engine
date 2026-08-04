import importlib.util
import os
import sys

from shard.core.entity import EntityManager, Entity
from shard.core.components import Script

# User-facing api, similar to engine but stripped to the minimum requirements for scripting
class ScriptingAPI:
    def __init__(self, engine):
        self.entity_manager = engine.managers.entity
        self.logger = engine.logger

        # For advanced, engine-breaking use only
        self.__engine = engine

    def get_component(self, entity, comp_name):
        match entity:
            case int():
                return self.entity_manager.entities[entity].components.get(comp_name)
            case Entity():
                return entity.components.get(comp_name)
        
    @property
    def engine(self):
        self.logger.log_warning("get_engine() is intended for advanced use only and can break the engine when used improperly. Prefer the provided ScriptingAPI instead.")
        return self.__engine

    @property
    def dt(self):
        return self.__engine.dt

def script(cls):
    cls.__is_script__ = True
    return cls

class ScriptSystem:
    def __init__(self, entity_manager: EntityManager, engine):
        self.entity_manager = entity_manager
        self.scripting_api = ScriptingAPI(engine)

        self.script_handles = {}
        self.next_handle = 0

        self.path_script_map = {}

    def add_script(self, eid, path: str):
        self.script_handles[self.next_handle] = path
        self.entity_manager.add_component(eid, Script(self.next_handle))
        self.next_handle += 1
        self.scripting_api.logger.log_debug(f"Loaded script at '{path}'")

    # Generator to lazily iterate over script components and get the module required by that script
    def get_script_components(self):
        for eid in self.entity_manager.query("Script"):
            entity = self.entity_manager.entities[eid]
            script_comp = entity.components["Script"]

            path = self.script_handles[script_comp.handle]

            script_cls = self.path_script_map.get(path)

            if script_cls is None:
                file_name, _ = os.path.splitext(os.path.basename(path))
                module_name = f"script_{script_comp.handle}_{file_name}"

                spec = importlib.util.spec_from_file_location(module_name, path)
                script_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(script_module)

                for obj in vars(script_module).values():
                    if isinstance(obj, type) and getattr(obj, "__is_script__", False):
                        script_cls = obj
                        break

                if script_cls is None:
                    raise RuntimeError(f"No @script class found in '{path}'")

                self.path_script_map[path] = script_cls

            yield entity, script_cls

    # start() callback: runs on start of play mode
    def start(self):
        for entity, script_cls in self.get_script_components():
            instance = script_cls()
            if hasattr(instance, "start"):
                instance.start(entity, self.scripting_api)

    # update() callback: runs once every frame
    def update(self):
        for entity, script_cls in self.get_script_components():
            instance = script_cls()
            if hasattr(instance, "update"):
                instance.update(entity, self.scripting_api)