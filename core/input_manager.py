import pygame

class InputManager:
    def __init__(self):
        self.prev_keys = pygame.key.get_pressed()
        self.current_keys = pygame.key.get_pressed()

        self.prev_mouse = pygame.mouse.get_pressed()
        self.current_mouse = pygame.mouse.get_pressed()

    def update(self):
        self.prev_keys = self.current_keys
        self.current_keys = pygame.key.get_pressed()

        self.prev_mouse = self.current_mouse
        self.current_mouse = pygame.mouse.get_pressed()

    def is_key_just_pressed(self, key_constant):
        return self.current_keys[key_constant] and not self.prev_keys[key_constant]
    
    def is_mouse_just_pressed(self, mouse_constant):
        return self.current_mouse[mouse_constant] and not self.prev_mouse[mouse_constant]
