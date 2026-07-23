from ..component import component

@component
class Name:
    __inspect__ = [
        "name",
        "tag"
    ]

    def __init__(self, name: str = "Empty", tag: str = "None"):
        self.entity = None

        self.name = name
        self.tag = tag