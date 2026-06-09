from collections import defaultdict

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