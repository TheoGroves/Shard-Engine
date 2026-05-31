class Transform:
    def __init__(self, pos, rot, scale):
        self.pos = pos
        self.rot = rot
        self.scale = scale

    @staticmethod
    def identity():
        return Transform((0,0,0), (0,0,0), (1,1,1))