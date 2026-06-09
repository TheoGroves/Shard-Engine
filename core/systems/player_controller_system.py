import pygame
import numpy as np
from ecs import EntityManager
from collisions.collision_solver import solve_capsule

class PlayerControllerSystem:
    def __init__(self, em: EntityManager, camera_obj, play_mode=True):
        self.em = em
        self.camera_obj = camera_obj  # The renderer's camera object
        self.play_mode = play_mode
        self.base_speed = 2.5
        self.sprint_speed = 5.0

    def update(self, dt, triangles, grid, gravity):
        keys = pygame.key.get_pressed()
        
        for eid in self.em.query("PlayerController", "CapsuleCollider", "Rigidbody", "Transform", "Input"):
            transform = self.em.entities[eid].components["Transform"]
            capsule = self.em.entities[eid].components["CapsuleCollider"]
            rigidbody = self.em.entities[eid].components["Rigidbody"]
            input_comp = self.em.entities[eid].components["Input"]
            
            move = np.zeros(3, dtype=np.float32)
            
            speed = self.sprint_speed if keys[pygame.K_LCTRL] else self.base_speed
            
            if keys[pygame.K_w]:
                move += self.camera_obj.front * speed * dt
            if keys[pygame.K_s]:
                move -= self.camera_obj.front * speed * dt
            if keys[pygame.K_a]:
                move -= self.camera_obj.right * speed * dt
            if keys[pygame.K_d]:
                move += self.camera_obj.right * speed * dt
            
            if keys[pygame.K_SPACE]:
                if self.play_mode and rigidbody.grounded:
                    rigidbody.velocity[1] += 5.0
                elif not self.play_mode:
                    move += self.camera_obj.world_up * speed * dt
            
            if keys[pygame.K_LSHIFT] and not self.play_mode:
                move -= self.camera_obj.world_up * speed * dt
            
            if self.play_mode:
                move[1] = 0
            
            transform.pos += move
            
            if self.play_mode and dt < 1:
                rigidbody.velocity[1] += gravity * dt
            
            if self.play_mode:
                transform.pos += rigidbody.velocity * dt
                
                rigidbody.grounded, _ = solve_capsule(
                    transform,
                    capsule,
                    triangles,
                    grid
                )
            
            if rigidbody.grounded and rigidbody.velocity[1] < 0:
                rigidbody.velocity[1] = 0
            
            self.camera_obj.pos = transform.pos
