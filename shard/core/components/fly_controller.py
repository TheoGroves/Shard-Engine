from ..component import component

@component
class FlyController:
    __inspect__ = {
        "move_speed": "float",
        "boost_speed": "float",
        "mouse_sensitivity": "float"
    }

    def __init__(self, move_speed=5.0, boost_speed=10.0, mouse_sensitivity=0.15):
        self.current_speed = 0
        self.move_speed = move_speed
        self.boost_speed = boost_speed
        self.mouse_sensitivity = mouse_sensitivity

        self.mouse_hidden = True
        self.escape_last_frame = False

    def serialize(self):
        return {
            "move_speed": self.move_speed,
            "boost_speed": self.boost_speed,
            "mouse_sensitivity": self.mouse_sensitivity
        }

    @classmethod
    def deserialize(cls, data, engine):
        return cls(data["move_speed"], data["boost_speed"], data["mouse_sensitivity"])