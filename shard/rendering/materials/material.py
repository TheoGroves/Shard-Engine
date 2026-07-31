class Material:
    def __init__(self):
        self.material = None

    def draw_inspector(self, inspector):
        raise NotImplementedError

    def serialize(self):
        raise NotImplementedError