from shard.scripting import script, ScriptingAPI, component

# Components store state but do not have any behaviour. 
@component
class ExampleComponent:
    # __inspect__ defines which variables are exposed to the inspector. 
    # A type is required to ensure the engine can distinguish between dynamically typed variables or specialized assets like Meshes and Textures.
    __inspect__ = {
        "value": "float"
    }

    def __init__(self, value=0.0):
        self.value = value

    # Components are responsible for their own serialization and deserialization.
    # Serialized values are then stored in a dictionary with a unique identifier which can be used to restore the data later.
    def serialize(self):
        return {
            "value": self.value
        }

    @classmethod
    def deserialize(cls, data, engine):
        return cls(data["value"])

# Scripts are stateless behaviours executed by entities.
# Persistent data should be stored in a component attached to the entity and requested using the ScriptingAPI
@script
class ExampleScript:
    # Called when play mode starts
    def start(self, entity, api: ScriptingAPI):
        api.logger.log_info(f"Hello World from entity {entity.eid}")

    # Called every single frame
    def update(self, entity, api: ScriptingAPI):
        pass