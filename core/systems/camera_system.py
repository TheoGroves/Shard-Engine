import pygame
from ecs import EntityManager
from core.systems import TransformSystem

class CameraSystem:
    def __init__(self, em: EntityManager, transform_system: TransformSystem):
        self.em = em
        self.ts = transform_system
        self.focused = False
        self.just_focused = False
        self.sensitivity = 5

    def update(self, keys, dt, ui_renderer):
        for eid in self.em.query("Camera", "Transform"):
            cam_entity = self.em.entities[eid]

            cam_t = cam_entity.components["Transform"]
            cam = cam_entity.components["Camera"]

            if not cam.active:
                continue
            
            cam_rot = self.ts.get_transform(eid).rot

            if keys[pygame.K_ESCAPE] and self.focused:
                self.focused = False
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)

            if pygame.mouse.get_pressed()[0] and not self.focused and not ui_renderer.check_ui_blocking():
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

                    cam_rot[1] += mx * self.sensitivity * dt
                    cam_rot[0] -= my * self.sensitivity * dt
                    cam_rot[0] = max(-89.0, min(89.0, cam_rot[0]))
                
                self.ts.set_rot(eid, cam_rot)