from ..component import component

@component
class Camera:
    def __init__(self, active: bool):
        self.entity = None

        self.active = active