import importlib.util
import os
from pathlib import Path
import inspect
import time
from functools import partial

from shard.core.entity import EntityManager, Entity
from shard.core.components import Script
from shard.core.component import COMPONENT_REGISTRY

# User-facing api, similar to engine but stripped to the minimum requirements for scripting
class ScriptingAPI:
    def __init__(self, engine):
        self.entity_manager = engine.managers.entity
        self.logger = engine.logger
        self.audio_engine = engine.audio_engine

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

    @property
    def player_input(self):
        return self.__engine.player_input

def script(cls=None, *, requires=None):
    if cls is None:
        return partial(script, requires=requires)

    if requires is None:
        requires = []

    cls.__is_script__ = True
    cls.__requires__ = requires
    return cls

class ScriptSystem:
    def __init__(self, entity_manager: EntityManager, engine):
        self.entity_manager = entity_manager
        self.scripting_api = ScriptingAPI(engine)

        self.script_handles = {}
        self.path_handle_map = {}
        self.next_handle = 0

        self.path_script_map = {}

        # Preload scripts and components
        self.preload()


    # Assign a path to a script handle when requested during preloading, returns whether script was preloaded or not
    def preload_script(self, path):
        if path in self.path_handle_map:
            self.scripting_api.logger.log_debug("Script already loaded at '{path}'")
            return False

        self.script_handles[self.next_handle] = path
        self.path_handle_map[path] = self.next_handle
        self.next_handle += 1
        return True
        
    def add_script(self, eid, path: str):
        self.script_handles[self.next_handle] = path
        self.path_handle_map[path] = self.next_handle
        self.entity_manager.add_component(eid, Script(self.next_handle))
        self.next_handle += 1
        self.scripting_api.logger.log_debug(f"Loaded script at '{path}'")

    def add_component(self, eid, comp_name):
        self.scripting_api.entity_manager.add_component_name(eid, comp_name)

    # Script preloading is required for user-components to be loaded immediately
    def preload(self):
        start = time.perf_counter()

        package = "scripts"
        package_path = Path(__file__).parent.parent.parent.parent / package

        self.scripting_api.logger.log_info(f"{package_path}")

        components_preloaded = 0
        scripts_preloaded = 0

        for file in package_path.glob("*.py"):
            if file.name.startswith("_"):
                continue

            module_name = f"{package}.{file.stem}"
            module = importlib.import_module(module_name)

            if self.preload_script(str(file)):
                scripts_preloaded += 1

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module_name and obj.__name__ in COMPONENT_REGISTRY:
                    components_preloaded += 1

        self.scripting_api.logger.log_info(f"Pre-loaded {components_preloaded} user-made components and {scripts_preloaded} user-made scripts")

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

    def validate_scripts(self):
        # Validate that every entity with scripts has all required components
        for entity, script in self.get_script_components():
            failed = False
            missing_components = []

            for req in script.__requires__:
                if not req in entity.components:
                    failed = True
                    missing_components.append(req)

            if failed:
                for missing in missing_components:
                    self.scripting_api.logger.log_error(f"The script '{script.__name__}' on entity '{self.scripting_api.get_component(entity, 'Name').name}' requires the component '{missing}'")
                    
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