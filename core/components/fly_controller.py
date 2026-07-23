from ..component import component

@component
class FlyController:
    __inspect__ = [
        "move_speed",
        "boost_speed",
        "mouse_sensitivity"
    ]

    def __init__(self):
        self.current_speed = 0
        self.move_speed = 5
        self.boost_speed = 10
        self.mouse_sensitivity = 0.15

        self.mouse_hidden = True
        self.escape_last_frame = False