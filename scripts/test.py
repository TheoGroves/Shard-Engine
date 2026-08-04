from shard.core.systems import script, ScriptingAPI

@script
class ExampleScript:
    # Called when play mode starts
    def start(self, entity, api: ScriptingAPI):
        api.logger.log_info(f"Hello World from entity {entity.eid}")

    # Called every single frame
    def update(self, entity, api: ScriptingAPI):
        pass