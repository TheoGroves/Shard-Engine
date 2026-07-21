from ..component import component

@component
class Name:
    def __init__(self, name: str, tag: str = "None"):
        self.name = name
        self.tag = tag