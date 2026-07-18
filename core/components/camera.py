from ..component import component

@component
class Camera:
    def __init__(self, active: bool):
        self.active = active