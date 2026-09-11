from shard.scripting import script, ScriptingAPI, component, Vec3, normalize, length

@component
class FirstPersonCameraComponent:
    __inspect__ = {
        "sensitivity": "float",
        "normal_speed": "float",
        "boost_speed": "float"
    }

    def __init__(self):
        self.sensitivity = 0.05
        self.current_speed = 5.0
        self.normal_speed = 5.0
        self.boost_speed = 10.0

    def serialize(self):
        return {
            "sensitivity": self.sensitivity,
            "current_speed": self.current_speed,
            "normal_speed": self.normal_speed,
            "boost_speed": self.boost_speed
        }

    @classmethod
    def deserialize(cls, data, engine):
        return cls()
        
@script(requires=["FirstPersonCameraComponent", "LinearBody"])
class FirstPersonCameraScript:
    def start(self, entity, api: ScriptingAPI):
        api.logger.log_info(f"Hello World from entity {entity.eid}")

    def update(self, entity, api: ScriptingAPI):
        controller = api.get_component(entity, "FirstPersonCameraComponent")

        t = api.get_component(entity, "Transform")
        linear = api.get_component(entity, "LinearBody")

        move_dir = Vec3(0,0,0)

        if api.player_input.forward:
            move_dir = move_dir + t.world_forward

        if api.player_input.backward:
            move_dir = move_dir - t.world_forward

        if api.player_input.right:
            move_dir = move_dir + t.world_right

        if api.player_input.left:
            move_dir = move_dir - t.world_right

        # Remove vertical movement and normalize
        move_dir.y = 0
        move_dir = normalize(move_dir)

        if api.player_input.jump:
            linear.velocity.y = 5

        if length(move_dir) > 0.0:
            t.pos = t.pos + normalize(move_dir) * controller.current_speed * api.dt

        t.rot.y -= api.player_input.mouse_dx * controller.sensitivity
        t.rot.x -= api.player_input.mouse_dy * controller.sensitivity

        if t.rot.x > 90: t.rot.x = 90
        if t.rot.x < -90: t.rot.x = -90