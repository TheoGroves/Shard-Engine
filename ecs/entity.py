from collections import defaultdict
import json 
import numpy as np

from .component import COMPONENT_REGISTRY
from core.material import Material
from core.mesh import Mesh

SERIALIZABLE_REGISTRY = {
    "Material": Material,
    "Mesh": Mesh
}

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
            self._next_eid = max(self._next_eid, eid + 1)
        else:
            eid = self._next_eid
            self._next_eid += 1

        self.entities[eid] = Entity()
        return eid
    
    def add_component(self, eid, component):
        type_name = type(component).__name__
        self.entities[eid].components[type_name] = component
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
    def deserialize_component(comp_data, ctx):
        comp_type = comp_data["type"]
        comp_class = COMPONENT_REGISTRY[comp_type]

        raw_data = comp_data["data"]

        if hasattr(comp_class, "deserialize"):
            return comp_class.deserialize(raw_data, ctx)

        final_data = {}

        for key, value in raw_data.items():
            if isinstance(value, dict) and "__type__" in value:
                if value["__type__"] == "ndarray":
                    final_data[key] = np.array(
                        value["__value__"],
                        dtype=np.float32
                    )
                else:
                    cls = SERIALIZABLE_REGISTRY[value["__type__"]]
                    if hasattr(cls, "deserialize"):
                        final_data[key] = cls.deserialize(value["__value__"], ctx)
                    else:
                        final_data[key] = cls(**value["__value__"])
            else:
                final_data[key] = value

        return comp_class(**final_data)

    @staticmethod
    def load_scene(em, path, ctx):
        import json

        with open(path, "r") as f:
            data = json.load(f)

        em.entities.clear()
        em.components.clear()
        em._next_eid = 0

        for eid_str, entity_data in data["entities"].items():
            eid = int(eid_str)
            em.create_entity(forced_eid=eid)

            for comp_data in entity_data["components"]:
                component = Deserializer.deserialize_component(comp_data, ctx)
                em.add_component(eid, component)