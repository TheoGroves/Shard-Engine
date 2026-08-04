from ..component import component

@component
class Script:
    __inspect__ = {
        "handle": "int"
    }

    def __init__(self, handle: int = 0):
        self.entity = None

        self.handle = handle

    def serialize(self):
        return {
            "handle": self.handle
        }

    @classmethod
    def deserialize(cls, data, engine):
        return cls(data["handle"])