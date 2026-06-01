import numpy as np

class Rigidbody:
    def __init__(self):
        self.velocity = np.zeros(3, dtype=np.float32)
        self.grounded = False