import moderngl
import pygame
import numpy as np
from loaders.texture_loader import load_texture

class UIElement:
    def __init__(self, x, y, width, height, ctx):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ctx = ctx

        self.vbo = None
        self.vao = None
        self.tex = None

        self.screen_size = None

        self.vertices = None

    def generate_vertices(self):
        return np.array([
            self.x*self.screen_size[0]-self.width/2, self.y*self.screen_size[1]-self.height/2, 0, 0,
            self.x*self.screen_size[0]+self.width/2, self.y*self.screen_size[1]-self.height/2, 1, 0,
            self.x*self.screen_size[0]+self.width/2, self.y*self.screen_size[1]+self.height/2, 1, 1,

            self.x*self.screen_size[0]-self.width/2, self.y*self.screen_size[1]-self.height/2, 0, 0,
            self.x*self.screen_size[0]+self.width/2, self.y*self.screen_size[1]+self.height/2, 1, 1,
            self.x*self.screen_size[0]-self.width/2, self.y*self.screen_size[1]+self.height/2, 0, 1
        ], dtype=np.float32)

    def update_vertices(self):
        self.vertices = self.generate_vertices()

    def move(self, x, y):
        self.x = x
        self.y = y
        self.update_vertices()

    def _set_tex(self, tex):
        if self.tex:
            self.tex.release()

        self.tex = tex

        if self.tex:
            self.tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
            self.tex.build_mipmaps()

class UIImage(UIElement):
    def __init__(self, x, y, width, height, ctx, tex_path):
        super().__init__(x, y, width, height, ctx)
        self.set_texture(tex_path)
    
    def set_texture(self, texture_path):
        self._set_tex(load_texture(self.ctx, texture_path, "assets/textures/MissingUI.png")[0])

class UIText(UIElement):
    def __init__(self, x, y, text: str, font: pygame.font.Font, ctx: moderngl.Context, colour=(255,255,255)):
        text_surf = font.render(text, True, colour)
        w, h = text_surf.get_size()

        super().__init__(x, y, w, h, ctx)
        self.text = text
        self.font = font
        self.colour = colour

        self.set_tex_from_surf(text_surf)

    def set_tex_from_surf(self, surface):
        data = pygame.image.tobytes(surface, "RGBA", False)

        self._set_tex(self.ctx.texture(size=surface.get_size(), components=4, data=data))

    def update_text(self, text):
        self.text = text
        text_surf = self.font.render(text, True, self.colour)

        self.width, self.height = text_surf.get_size()
        self.update_vertices()

        self.vbo.orphan()
        self.vbo.write(self.vertices.astype("f4").tobytes())

        self.set_tex_from_surf(text_surf)