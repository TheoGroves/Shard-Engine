from shard.scripting import script, ScriptingAPI, component, Vec3

# Components store state but do not have any behaviour. 
@component
class ExampleComponent:
    # __inspect__ defines which variables are exposed to the inspector. 
    # A type is required to ensure the engine can distinguish between dynamically typed variables or specialized assets like Meshes and Textures.
    __inspect__ = {
        "value": "float"
    }

    def __init__(self):
        self.value = 0
        self.source = 0

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
        test = api.audio_engine.load_audio("assets/audio/Test.wav")
        t = api.get_component(entity, "Transform")
        source = api.audio_engine.play(test, t.world_pos, t.velocity)
        api.get_component(entity, "ExampleComponent").source = source

    # Called every single frame
    def update(self, entity, api: ScriptingAPI):
        t = api.get_component(entity, "Transform")
        source = api.get_component(entity, "ExampleComponent").source
        api.audio_engine.update_source(source, t.world_pos, t.velocity)