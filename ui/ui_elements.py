import moderngl
import pygame
import numpy as np
from PIL import Image
from loaders.texture_loader import load_texture

ANCHORS = {
    "centre": (0.5, 0.5),
    "left": (0.0, 0.5),
    "right": (1.0, 0.5),
    "top": (0.5, 0.0),
    "bottom": (0.5, 1.0),
    "top_left": (0.0, 0.0),
    "top_right": (1.0, 0.0),
    "bottom_left": (0.0, 1.0),
    "bottom_right": (1.0, 1.0),
}

class UIElement:
    def __init__(self, x, y, width, height, ctx, anchor="centre"):
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

        self.anchor = anchor
        self.brightness = 1.0

    def generate_vertices(self):
        cx = self.x * self.screen_size[0]
        cy = self.y * self.screen_size[1]

        ax, ay = ANCHORS[self.anchor]

        left = cx - ax * self.width
        top  = cy - ay * self.height

        return np.array([
            left, top, 0, 0,
            left + self.width, top, 1, 0,
            left + self.width, top + self.height, 1, 1,

            left, top, 0, 0,
            left + self.width, top + self.height, 1, 1,
            left, top + self.height, 0, 1
        ], dtype=np.float32)
    
    def get_anchor_offset(self):
        ax, ay = ANCHORS.get(self.anchor, (0.5, 0.5))

        return (
            (ax - 0.5) * self.width,
            (ay - 0.5) * self.height
        )

    def update_vertices(self):
        self.vertices = self.generate_vertices()

    def move(self, x, y):
        self.x = x
        self.y = y
        self.update_vertices()

    def mouse_over(self) -> bool:
        mx, my = pygame.mouse.get_pos()

        cx = self.x * self.screen_size[0]
        cy = self.y * self.screen_size[1]

        ax, ay = ANCHORS[self.anchor]

        left = cx - ax * self.width
        top  = cy - ay * self.height

        return (
            left <= mx <= left + self.width and
            top <= my <= top + self.height
        )
    
    def is_blocking(self):
        return self.mouse_over()

    def _set_tex(self, tex):
        if self.tex:
            self.tex.release()

        self.tex = tex

        if self.tex:
            self.tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
            self.tex.build_mipmaps()

class UIImage(UIElement):
    def __init__(self, x, y, width, height, ctx, tex_path, anchor="centre"):
        super().__init__(x, y, width, height, ctx, anchor)
        self.set_texture(tex_path)
    
    def set_texture(self, texture_path):
        self._set_tex(load_texture(self.ctx, texture_path, "assets/textures/MissingUI.png")[0])

class UIText(UIElement):
    def __init__(self, x, y, text: str, font: pygame.font.Font, ctx: moderngl.Context, colour=(255,255,255), anchor="centre"):
        text_surf = font.render(text, True, colour)
        w, h = text_surf.get_size()

        super().__init__(x, y, w, h, ctx, anchor)
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

class UIFloat(UIText):
    def __init__(self, x, y, descriptor: str, value: float, font: pygame.font.Font, ctx: moderngl.Context, colour=(255,255,255), anchor="centre"):
        super().__init__(x, y, f"{value}", font, ctx, colour, anchor)
        self.descriptor = descriptor
        self.value = value

        self.mouse_held = False
        self.init_mx = 0
        self.init_val = 0

    def update(self):
        mouse_on = self.mouse_over()

        if not self.mouse_held and mouse_on and pygame.mouse.get_pressed()[0]:
            mx, _ = pygame.mouse.get_pos()
            self.mouse_held = True

            self.init_mx = mx
            self.init_val = self.value

        if self.mouse_held:
            if pygame.mouse.get_pressed()[0]:
                mx, _ = pygame.mouse.get_pos()
                diff = mx - self.init_mx
                self.value = self.init_val + (diff / 100)

            else:
                self.mouse_held = False

        self.update_text(f"{self.descriptor} {self.value:.1f}")

    def is_blocking(self):
        return super().is_blocking() or self.mouse_held
    
class UIButton(UIImage):
    def __init__(self, x, y, scale, ctx, tex_path, anchor="centre"):
        with Image.open(tex_path) as img:
            width, height = img.size
        super().__init__(x, y, width*scale, height*scale, ctx, tex_path, anchor)
        self.brightness = 0.5

    def update(self):
        self.brightness = 0.5
        if self.mouse_over() and pygame.mouse.get_pressed()[0]:
            self.brightness = 1.0
            return True
        return False