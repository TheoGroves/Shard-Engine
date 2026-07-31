from ..component import component

@component
class Name:
    __inspect__ = {
        "name": "string",
        "tag": "string"
    }

    def __init__(self, name: str = "Empty", tag: str = "None"):
        self.entity = None

        self.name = name
        self.tag = tag

    def serialize(self):
        return {
            "name": self.name,
            "tag": self.tag
        }

    @classmethod
    def deserialize(cls, data, engine):
        return cls(data["name"], data["tag"])