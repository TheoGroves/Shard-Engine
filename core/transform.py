class Transform:
    def __init__(self, pos=(0,0,0), rot=(0,0,0), scale=(1,1,1)):
        self.pos = pos
        self.rot = rot
        self.scale = scale

    @staticmethod
    def identity():
        return Transform((0,0,0), (0,0,0), (1,1,1))