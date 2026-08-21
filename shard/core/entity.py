from collections import defaultdict
import json
import time
import shutil

from .component import COMPONENT_REGISTRY

class Entity:
    def __init__(self, eid: int):
        self.eid = eid
        self.components = {}

class EntityManager:
    def __init__(self):
        self.entities = {}
        self.components = defaultdict(dict)
        self._next_eid = 0

    def create_entity(self, forced_eid=None):
        if forced_eid is not None:
            if forced_eid in self.entities:
                raise ValueError(f"Entity {forced_eid} already exists.")
            eid = forced_eid
            if eid >= self._next_eid:
                self._next_eid = eid + 1
        else:
            eid = self._next_eid
            self._next_eid += 1

        entity = Entity(eid)
        self.entities[eid] = entity
        return eid, entity
    
    def add_component(self, eid, component):
        component.entity = eid

        type_name = type(component).__name__
        self.entities[eid].components[type_name] = component
        self.components[type_name][eid] = component

    def add_component_name(self, eid, component_name):
        component = COMPONENT_REGISTRY[component_name]()

        component.entity = eid

        self.entities[eid].components[component_name] = component
        self.components[component_name][eid] = component

    def add_component_direct(self, entity, eid, component):
        component.entity = eid

        type_name = type(component).__name__
        entity.components[type_name] = component
        self.components[type_name][eid] = component

    def remove_component(self, eid, component_type):
        type_name = component_type.__name__ if isinstance(component_type, type) else component_type

        if eid in self.entities and type_name in self.entities[eid].components:
            del self.entities[eid].components[type_name]

            del self.components[type_name][eid]

            if not self.components[type_name]:
                del self.components[type_name]

    def remove_entity(self, eid):
        if eid in self.entities:
            for type_name in self.entities[eid].components.keys():
                del self.components[type_name][eid]
            del self.entities[eid]

    def query(self, *component_types):
        if not component_types:
            return []

        sets = [set(self.components[ct].keys()) for ct in component_types]
        return set.intersection(*sets)
    
    def clear(self):
        self.entities = {}
        self.components = defaultdict(dict)
        self._next_eid = 0

class Serializer:
    @staticmethod
    def serialize_component(comp):
        return {
            "type": type(comp).__name__,
            "data": comp.serialize()
        }

    @staticmethod
    def serialize_entity(entity):
        return {
            "components": [
                Serializer.serialize_component(comp) for comp in entity.components.values()
            ]
        }

    @staticmethod
    def serialize_scene(em: EntityManager):
        return {
            "entities": {
                eid: Serializer.serialize_entity(entity) for eid, entity in em.entities.items()
            }
        }

    @staticmethod
    def create_backup(path):
        shutil.copy2(path, f"{path}.bak")

    @staticmethod
    def save_scene(em: EntityManager, path, logger):
        start = time.perf_counter()
        Serializer.create_backup(path)

        with open(path, "w") as f:
            json.dump(Serializer.serialize_scene(em), f, indent=4)

        logger.log_info(f"Scene saved in {(time.perf_counter()-start)*1000:.1f}ms")


class Deserializer:
    @staticmethod
    def deserialize_component(comp_data, engine):
        comp_type = comp_data["type"]
        comp_class = COMPONENT_REGISTRY[comp_type]
        data = comp_data["data"]

        return comp_class.deserialize(data, engine)

    @staticmethod
    def load_scene(em: EntityManager, engine, path, logger):
        start = time.perf_counter()
        with open(path, "r") as f:
            data = json.load(f)

        em.entities.clear()
        em.components.clear()
        em._next_eid = 0

        for eid_str, entity_data in data["entities"].items():
            eid = int(eid_str)
            _, entity = em.create_entity(eid)

            for comp_data in entity_data["components"]:
                component = Deserializer.deserialize_component(comp_data, engine)
                em.add_component_direct(entity, eid, component)

        logger.log_info(f"Scene loaded in {(time.perf_counter()-start)*1000:.1f}ms")

    @staticmethod
    def restore_backup(em: EntityManager, engine, path, logger):
        shutil.copy2(f"{path}.bak", path)
        Deserializer.load_scene(em, engine, path, logger)
        