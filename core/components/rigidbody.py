import numpy as np
from ecs import component
 
@component
class Rigidbody:
    def __init__(self, velocity=np.zeros(3, dtype=np.float32), grounded=False):
        self.velocity = velocity
        self.grounded = grounded