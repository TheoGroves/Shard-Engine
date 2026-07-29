from ..component import component

@component
class Camera:
    __inspect__ = [
        "active"
    ]
    def __init__(self, active: bool = False):
        self.entity = None

        self.active = active