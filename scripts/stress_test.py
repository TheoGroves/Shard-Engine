from shard.scripting import script, ScriptingAPI, component, Vec3

# Components store state but do not have any behaviour. 
@component
class StressTestComponent:
    __inspect__ = {
        "total_entities": "int",
        "max_entities": "int"
    }

    def __init__(self, max_entities=0):
        self.total_entities = 0
        self.max_entities = max_entities

    def serialize(self):
        return {
            "total_entities": self.total_entities,
            "max_entities": self.max_entities
        }

    @classmethod
    def deserialize(cls, data, engine):
        return cls(data["max_entities"])

@script(requires=["StressTestComponent"])
class StressTest:
    # Called when play mode starts
    def start(self, entity, api: ScriptingAPI):
        pass

    # Called every single frame
    def update(self, entity, api: ScriptingAPI):
        stress_test = api.get_component(entity, "StressTestComponent")

        while stress_test.max_entities > stress_test.total_entities:
            api.create_entity()
            stress_test.total_entities += 1