class Transform:
    def __init__(self, pos=(0,0,0), rot=(0,0,0), scale=(1,1,1)):
        self.pos = pos
        self.rot = rot
        self.scale = scale

    def set_pos(self, pos):
        self.pos = pos

    def set_rot(self, rot):
        self.rot = rot

    def set_scale(self, scale):
        self.scale = scale

    @staticmethod
    def identity():
        return Transform((0,0,0), (0,0,0), (1,1,1))