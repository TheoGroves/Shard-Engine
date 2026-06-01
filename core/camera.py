import numpy as np
import pygame

def normalize(v):
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / n

class Camera:
    def __init__(self, position=(0, 0, 5), yaw=-90.0, pitch=0.0):
        self.position = np.array(position, dtype=np.float32)

        self.yaw = yaw
        self.pitch = pitch

        self.front = np.array([0, 0, -1], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.array([1, 0, 0], dtype=np.float32)

        self.world_up = np.array([0, 1, 0], dtype=np.float32)

        self.speed = 2.5
        self.sensitivity = 5.0

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        self.focused = True
        self.just_focused = False

        self.update_vectors()

    def process_inputs(self, keys, dt):
        if keys[pygame.K_ESCAPE] and self.focused:
            self.focused = False
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)

        if pygame.mouse.get_pressed()[0] and not self.focused:
            self.focused = True
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)
            self.just_focused = True
        
        if self.focused:
            if self.just_focused:
                pygame.mouse.get_rel()
                self.just_focused = False
            else:
                mx, my = pygame.mouse.get_rel()
                self.yaw += mx * self.sensitivity * dt
                self.pitch -= my * self.sensitivity * dt

                self.pitch = max(-89.0, min(89.0, self.pitch))

            self.update_vectors()

    def update_vectors(self):
        yaw_rad = np.radians(self.yaw)
        pitch_rad = np.radians(self.pitch)

        front = np.array([
            np.cos(yaw_rad) * np.cos(pitch_rad),
            np.sin(pitch_rad),
            np.sin(yaw_rad) * np.cos(pitch_rad)
        ], dtype=np.float32)

        self.front = normalize(front)
        self.right = normalize(np.cross(self.front, self.world_up))
        self.up = normalize(np.cross(self.right, self.front))