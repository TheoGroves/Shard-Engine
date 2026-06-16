from collections import defaultdict
import json 
import numpy as np
import inspect
import time

from .component import COMPONENT_REGISTRY
from core.material import Material
from core.mesh import Mesh

SERIALIZABLE_REGISTRY = {
    "Material": Material,
    "Mesh": Mesh
}

_SIGNATURE_CACHE = {}

def call_maybe_with(func, *args, **kwargs):
    if func not in _SIGNATURE_CACHE:
        sig = inspect.signature(func)
        _SIGNATURE_CACHE[func] = "asset_manager" in sig.parameters

    if not _SIGNATURE_CACHE[func]:
        kwargs.pop("asset_manager", None)

    return func(*args, **kwargs)

class Entity:
    def __init__(self):
        self.components = {}

class EntityManager:
    def __init__(self):
        self.entities = {}
        self.components = defaultdict(dict)
        self._next_eid = 0

    def create_entity(self, forced_eid=None):
        if forced_eid is not None:
            eid = forced_eid
            if eid >= self._next_eid:
                self._next_eid = eid + 1
        else:
            eid = self._next_eid
            self._next_eid += 1

        entity = Entity()
        self.entities[eid] = entity
        return eid, entity
    
    def add_component(self, eid, component):
        type_name = type(component).__name__
        self.entities[eid].components[type_name] = component
        self.components[type_name][eid] = component

    def add_component_direct(self, entity, eid, component):
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
    def serialize_component(component):
        if hasattr(component, "serialize"):
            return {
                "type": type(component).__name__,
                "data": component.serialize()
            }
        
        data = {}

        for key, value in vars(component).items():
            if isinstance(value, np.ndarray):
                data[key] = {
                        "__type__": "ndarray",
                        "__value__": value.tolist()
                    }
            elif hasattr(value, "serialize"):
                data[key] = {
                    "__type__": type(value).__name__,
                    "__value__": value.serialize()
                }
            elif hasattr(value, "__dict__"):
                data[key] = {
                    "__type__": type(value).__name__,
                    "__value__": vars(value)
                }
            else:
                data[key] = value

        return {
            "type": type(component).__name__,
            "data": data
        }

    @staticmethod
    def serialize_entity(entity):
        return {
            "components": [
                Serializer.serialize_component(comp)
                for comp in entity.components.values()
            ]
        }

    @staticmethod
    def serialize_scene(em):
        return {
            "entities": {
                eid: Serializer.serialize_entity(entity)
                for eid, entity in em.entities.items()
            }
        }

    @staticmethod
    def save_scene(em, path):
        with open(path, "w") as f:
            json.dump(Serializer.serialize_scene(em), f, indent=4)

class Deserializer:
    @staticmethod
    def deserialize_component(comp_data, ctx, asset_manager):
        comp_type = comp_data["type"]
        comp_class = COMPONENT_REGISTRY[comp_type]
        raw_data = comp_data["data"]

        if hasattr(comp_class, "deserialize"):
            deserialize_method = getattr(comp_class, "deserialize")
            return call_maybe_with(deserialize_method, raw_data, ctx, asset_manager=asset_manager)

        final_data = {}
        for key, value in raw_data.items():
            if isinstance(value, dict) and "__type__" in value:
                val_type = value["__type__"]
                if val_type == "ndarray":
                    final_data[key] = np.array(value["__value__"], dtype=np.float32)
                else:
                    cls = SERIALIZABLE_REGISTRY[val_type]
                    if hasattr(cls, "deserialize"):
                        custom_method = getattr(cls, "deserialize")
                        final_data[key] = call_maybe_with(custom_method, value["__value__"], ctx, asset_manager=asset_manager)
                    else:
                        final_data[key] = cls(**value["__value__"])
            else:
                final_data[key] = value

        return comp_class(**final_data)

    @staticmethod
    def load_scene(em, path, ctx, asset_manager, profile=False):
        t_start = time.perf_counter()
        with open(path, "r") as f:
            data = json.load(f)
        print(f"JSON parsing took {(time.perf_counter()-t_start)*1000:.1f}ms")

        t_clear = time.perf_counter()
        em.entities.clear()
        em.components.clear()
        em._next_eid = 0
        print(f"ECS clearing took {(time.perf_counter()-t_clear)*1000:.1f}ms")

        total_entities = 0
        total_components = 0
        entity_creation_time = 0.0
        deserialization_time = 0.0
        ecs_addition_time = 0.0

        t_loop_start = time.perf_counter()

        component_stats = defaultdict(lambda: {
            "count": 0,
            "deserialize_time": 0.0,
            "add_time": 0.0
        })

        deserialize_comp = Deserializer.deserialize_component
        add_comp_direct = em.add_component_direct
        create_ent = em.create_entity
        
        for eid_str, entity_data in data["entities"].items():
            total_entities += 1
            
            t_ent = time.perf_counter()
            eid = int(eid_str)
            _, entity = create_ent(forced_eid=eid)
            entity_creation_time += time.perf_counter() - t_ent

            for comp_data in entity_data["components"]:
                total_components += 1

                comp_type = comp_data.get("type", "Unknown")

                t_deser = time.perf_counter()
                component = deserialize_comp(comp_data, ctx, asset_manager)
                deser_time = time.perf_counter() - t_deser
                deserialization_time += deser_time

                t_add = time.perf_counter()
                add_comp_direct(entity, eid, component)
                add_time = time.perf_counter() - t_add
                ecs_addition_time += add_time

                stats = component_stats[comp_type]
                stats["count"] += 1
                stats["deserialize_time"] += deser_time
                stats["add_time"] += add_time

                if profile:
                    print(
                        f"[{comp_type}] "
                        f"deserialize={deser_time*1000:.3f}ms "
                        f"add={add_time*1000:.3f}ms "
                        f"data_size={len(str(comp_data))}"
                    )

        total_loop_time = (time.perf_counter() - t_loop_start) * 1000

        if profile:
            print(f"Scene Loading:         {total_loop_time:.1f}ms")
            print(f"Processed:             {total_entities} entities, {total_components} components")
            print(f"-  Entity creation:    {entity_creation_time*1000:.1f}ms")
            print(f"-  Deserialization:    {deserialization_time*1000:.1f}ms")
            print(f"-  ECS Add component:  {ecs_addition_time*1000:.1f}ms")