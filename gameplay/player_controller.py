import numpy as np
import pygame
from collisions.collision_solver import solve_capsule

class PlayerController:
    def __init__(self, camera, player_rb, player_capsule):
        self.camera = camera
        self.grounded = False
        self.player_rb = player_rb
        self.player_capsule = player_capsule

        self.speed = 2.5

    def update(self, keys, dt, triangles, grid, GRAVITY, PLAY_MODE):
        move = np.zeros(3)

        if keys[pygame.K_w]:
            move += self.camera.front * self.speed * dt
        if keys[pygame.K_s]:
            move -= self.camera.front * self.speed * dt
        if keys[pygame.K_a]:
            move -= self.camera.right * self.speed * dt
        if keys[pygame.K_d]:
            move += self.camera.right * self.speed * dt
        if keys[pygame.K_SPACE]:
            if PLAY_MODE and self.grounded:
                self.player_rb.velocity += self.camera.world_up * 5
            else:
                move += self.camera.world_up * self.speed * dt
        if keys[pygame.K_LSHIFT]:
            if not PLAY_MODE:
                move -= self.camera.world_up * self.speed * dt

        if keys[pygame.K_LCTRL]:
            self.speed = 5.0
        else:
            self.speed = 2.5

        if PLAY_MODE:
            move[1] = 0

        self.player_capsule.position += move

        if dt < 1 and PLAY_MODE:
            self.player_rb.velocity[1] += GRAVITY * dt

        if PLAY_MODE:
            self.player_capsule.position += self.player_rb.velocity * dt

            self.grounded, normal = solve_capsule(
                self.player_capsule,
                triangles,
                grid
            )

        if self.grounded:
            if self.player_rb.velocity[1] < 0:
                self.player_rb.velocity[1] = 0

        self.camera.position = self.player_capsule.position