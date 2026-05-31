import numpy as np

class Capsule:
    def __init__(self, radius=0.3, height=1.8, offset=0):
        self.radius = radius
        self.height = height
        self.offset=offset

        self.position = np.zeros(3, dtype=np.float32)

    def get_segment(self):
        half = max(0.0, self.height * 0.5 - self.radius)

        p0 = self.position + np.array([0, -half+self.offset, 0], dtype=np.float32)
        p1 = self.position + np.array([0, half+self.offset, 0], dtype=np.float32)

        return p0, p1