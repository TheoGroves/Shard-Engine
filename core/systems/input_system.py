import pygame
import numpy as np
from ecs import EntityManager

class InputSystem:
    def __init__(self, em: EntityManager):
        self.em = em
        self.keys = {}

    def update(self):
        self.keys = pygame.key.get_pressed()
        
        for eid in self.em.query("Input"):
            input_comp = self.em.entities[eid].components["Input"]
            input_comp.keys = self.keys
            
            move = np.zeros(3, dtype=np.float32)
            if self.keys[pygame.K_w]:
                move[2] -= 1
            if self.keys[pygame.K_s]:
                move[2] += 1
            if self.keys[pygame.K_a]:
                move[0] -= 1
            if self.keys[pygame.K_d]:
                move[0] += 1
            
            if np.linalg.norm(move) > 0:
                move = move / np.linalg.norm(move)
            
            input_comp.move_direction = move
