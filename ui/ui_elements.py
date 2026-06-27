import moderngl
import pygame
import numpy as np
from PIL import Image
from loaders.texture_loader import load_texture

# Anchors modify where the quad is rendered from the element position
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

# Potential colours for the line graph
COLOURS = [
    (249, 237, 105),
    (240, 138, 93),
    (184, 59, 94),
    (106, 44, 112)
]

class UIElement:
    """Base Class for UI that manages the basic quad, texture and UI inputs."""
    def __init__(self, x, y, width, height, ctx, anchor="centre"):
        # Quad data
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # OpenGL context
        self.ctx = ctx

        # Quad buffers and texture
        self.vbo = None
        self.vao = None
        self.tex = None

        self.screen_size = None

        # Quad vertices
        self.vertices = None

        # Position anchor
        self.anchor = anchor

        # UI colour modification
        self.brightness = 1.0

    def generate_vertices(self):
        """Generate the quad's vertices based on screen size and the UI's anchor."""

        # Calculate position based on screen size and anchor
        cx = self.x * self.screen_size[0]
        cy = self.y * self.screen_size[1]

        ax, ay = ANCHORS[self.anchor]

        left = cx - ax * self.width
        top  = cy - ay * self.height

        # Return array of vertex positions and indices
        return np.array([
            left, top, 0, 0,
            left + self.width, top, 1, 0,
            left + self.width, top + self.height, 1, 1,

            left, top, 0, 0,
            left + self.width, top + self.height, 1, 1,
            left, top + self.height, 0, 1
        ], dtype=np.float32)
    
    def get_anchor_offset(self):
        """Get the position offset of the quad based on quad size and the anchor."""
        
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
        """Check if the mouse overlaps the quad using AABB."""
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
        """
        Returns whether the UI element should block input.
        
        Default implementation blocks input when mouse is over the element.
        Subclasses can override this function to provide custom blocking conditions.
        """
        return self.mouse_over()

    def _set_tex(self, tex):
        """Release the current texture and replace it with a new ModernGL texture."""
        if self.tex:
            self.tex.release()

        self.tex = tex

        if self.tex:
            self.tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
            self.tex.build_mipmaps()

class UIImage(UIElement):
    """A UI Element that displays an image."""

    def __init__(self, x, y, width, height, ctx, tex_path, anchor="centre"):
        super().__init__(x, y, width, height, ctx, anchor)
        self.set_texture(tex_path)
    
    def set_texture(self, texture_path):
        """
        Loads a texture from the specified file path.

        Falls back on MissingUI.png when specified file path doesn't exist.
        """
        self._set_tex(load_texture(self.ctx, texture_path, "assets/textures/MissingUI.png")[0])

class UIText(UIElement):
    """A UI Element that renders text as a texture."""
    def __init__(self, x, y, text: str, font: pygame.font.Font, ctx: moderngl.Context, colour=(255,255,255), anchor="centre"):
        text_surf = font.render(text, True, colour)
        w, h = text_surf.get_size()

        super().__init__(x, y, w, h, ctx, anchor)
        self.text = text
        self.font = font
        self.colour = colour

        self.set_tex_from_surf(text_surf)

    def set_tex_from_surf(self, surface):
        """Create and set a texture from a Pygame surface."""
        data = pygame.image.tobytes(surface, "RGBA", False)

        self._set_tex(self.ctx.texture(size=surface.get_size(), components=4, data=data))

    def update_text(self, text):
        """
        Update displayed text.

        Regenerate the texture, update quad size and refresh the vertex buffer.
        """
        self.text = text
        text_surf = self.font.render(text, True, self.colour)

        self.width, self.height = text_surf.get_size()
        self.update_vertices()

        # Reallocate buffer memory to prevent stalls
        self.vbo.orphan()

        self.vbo.write(self.vertices.astype("f4").tobytes())

        self.set_tex_from_surf(text_surf)

class UIFloat(UIText):
    """A draggable UI Text element that modifies a float value."""
    def __init__(self, x, y, descriptor: str, value: float, font: pygame.font.Font, ctx: moderngl.Context, colour=(255,255,255), anchor="centre"):
        super().__init__(x, y, f"{value}", font, ctx, colour, anchor)
        self.descriptor = descriptor
        self.value = value

        self.mouse_held = False
        self.init_mx = 0
        self.init_val = 0

    def update(self):
        """
        Handle mouse interaction with the quad and update the displayed value.

        Allows the user to drag on the quad to modify the value, updating every frame.
        """
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

        return self.value

    def is_blocking(self):
        """Block input while dragging or mouse is held."""
        return super().is_blocking() or self.mouse_held
    
class UIButton(UIImage):
    """A clickable UI Image element that returns True when pressed."""
    def __init__(self, x, y, scale, ctx, tex_path, anchor="centre"):
        with Image.open(tex_path) as img:
            width, height = img.size
        super().__init__(x, y, width*scale, height*scale, ctx, tex_path, anchor)
        self.brightness = 0.5

    def update(self):
        """
        Handle button presses and feedback.

        Returns True when pressed and False when not.
        """
        self.brightness = 0.5
        if self.mouse_over() and pygame.mouse.get_pressed()[0]:
            self.brightness = 1.0
            return True
        return False

class UILineGraph(UIElement):
    """
    A real-time graph UI Element that displays multiple values.

    Stores a fixed length buffer per line. 
    Renders average, maximum, and the historical line data on a Pygame surface, uploaded to a ModernGL texture.
    """
    def __init__(self, x, y, width, height, num_lines, ctx, anchor="centre"):
        self.num_lines = num_lines

        self.values = [[0] * 150 for _ in range(self.num_lines)]
        self.names = [f"Line {i}" for i in range(self.num_lines)]
        self.maximum = 1

        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 15)

        super().__init__(x, y, width, height, ctx, anchor)

        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self._dirty = True

    def add_value(self, value, line, name=None):
        """
        Add a new data point to the graph for a specific line and updates scaling based on maximum.

        Maintains the fixed buffer, pushing to one end and popping from the other.
        Updates the graph maximum to ensure graph stays in the UI bounds.
        """

        if name is not None:
            self.names[line] = name

        self.values[line].append(value)
        self.values[line].pop(0)

        self.maximum = max(max(line_vals) for line_vals in self.values)*1.15

    def get_avg(self, line: int):
        """Returns the average of a specific line buffer."""
        return sum(self.values[line])/len(self.values[line])
    
    def get_max(self, line: int):
        """Returns the maximum of a specific line buffer."""
        return max(self.values[line])

    def render_to_surface(self):
        """
        Render the graph onto a Pygame surface.

        This draws:
        - Background
        - Line buffers
        - Average and Maximum indicators
        - Legent
        - Axis Guide
        """
        self.surface.fill((0, 0, 0, 0))

        w, h = self.width, self.height

        graph_left = 50
        graph_width = w - graph_left - 5

        # Draw Background
        pygame.draw.rect(self.surface, (50, 50, 50, 40), (0, 0, w, h))

        max_val = self.maximum if self.maximum != 0 else 1

        # Draw each line buffer fitted into the quad
        for line_index, line_vals in enumerate(self.values):
            # Calculate maximum and average values for the line buffers
            average_val = self.get_avg(line_index)
            maximum_val = self.get_max(line_index)

            avg_h = h - (average_val / max_val) * h
            max_h = h - (maximum_val / max_val) * h

            # Draw average line and value next to the axis
            pygame.draw.line(
                self.surface,
                (170, 170, 170, 160),
                (graph_left-5, avg_h),
                (w, avg_h),
                1
            )

            max_string = f"{maximum_val:.1f}"
            max_text = self.font.render(max_string, True, (255, 255, 255))

            tr1 = max_text.get_rect()
            tr1.left = 10
            tr1.centery = max_h
            tr1 = tr1.inflate(5, 5)

            pygame.draw.rect(self.surface, (50, 50, 50, 150), tr1)

            self.surface.blit(max_text, (10, max_h-(self.font.size(max_string)[1]/2)))

            avg_string = f"{average_val:.1f}"
            avg_text = self.font.render(avg_string, True, (255, 255, 255))

            # Draw maximum line and value next to the axis
            pygame.draw.line(
                self.surface,
                (170, 170, 170, 160),
                (graph_left-5, max_h),
                (w, max_h),
                1
            )

            tr2 = avg_text.get_rect()
            tr2.left = 10
            tr2.centery = avg_h
            tr2 = tr2.inflate(5, 5)

            pygame.draw.rect(self.surface, (50, 50, 50, 150), tr2)

            self.surface.blit(avg_text, (10, avg_h-(self.font.size(avg_string)[1]/2)))

            # Calculate positions of line buffer points on the quad
            points = []
            for i, value in enumerate(line_vals):
                x = graph_left + (i / (len(line_vals) - 1)) * graph_width
                y = h - (value / max_val) * h
                points.append((x, y))
            
            # Draw the line buffer with the relevant colour to distinguish them 
            pygame.draw.lines(
                self.surface,
                COLOURS[line_index % len(COLOURS)],
                False,
                points,
                2
            )

        # Draw axis
        pygame.draw.line(self.surface, (170, 170, 170), (graph_left, h-1), (graph_left, 0))
        pygame.draw.line(self.surface, (170, 170, 170), (graph_left, h-1), (w, h-1))

        # Draw legent and a background to differentiate it from the rest of the line graph
        legend_x = 10+graph_left
        legend_y = 5
        line_height = 18

        max_text_width = 0
        for name in self.names:
            text_width = self.font.size(name)[0]
            max_text_width = max(max_text_width, text_width)

        legend_width = 20 + max_text_width + 5
        legend_height = len(self.names) * line_height + 5

        pygame.draw.rect(
            self.surface,
            (30, 30, 30, 50),
            (legend_x - 3, legend_y - 3, legend_width, legend_height)
        )

        pygame.draw.rect(
            self.surface,
            (255, 255, 255, 122),
            (legend_x - 3, legend_y - 3, legend_width, legend_height),
            1
        )

        # Draw colours next to the legend to determine which line matches the text
        current_y = legend_y
        for i, name in enumerate(self.names):
            colour = COLOURS[i % len(COLOURS)]

            pygame.draw.rect(self.surface, colour, (legend_x, current_y, 10, 10))

            text = self.font.render(name, True, (255, 255, 255))
            self.surface.blit(text, (legend_x + 15, current_y - 2))

            current_y += line_height

        self._dirty = True

    def update_texture(self):
        """
        Convert rendered surface to a ModernGL texture then upload to GPU.

        Skips update if no changes have occured.
        """

        if not self._dirty:
            return

        data = pygame.image.tobytes(self.surface, "RGBA", False)

        self._set_tex(
            self.ctx.texture(
                size=self.surface.get_size(),
                components=4,
                data=data
            )
        )

        self._dirty = False

    def update(self):
        """Render graph and upload to GPU."""
        self.render_to_surface()
        self.update_texture()

class UIScrollGrid(UIElement):
    """**UNFINISHED:** A Scrollable grid UI Element that contains items which are rendered in a moving grid."""
    def __init__(self, x, y, width, height, ctx, anchor="centre"):
        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 18)

        self._items = []

        super().__init__(x, y, width, height, ctx, anchor)

        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self._dirty = True


    def add_item(self, item):
        self._items.append(item)

    def render_to_surface(self):
        self.surface.fill((0, 0, 0, 0))

        w, h = self.width, self.height

        pygame.draw.rect(self.surface, (100, 100, 100, 180), (0, 0, w, h))

        self._dirty = True

    def update_texture(self):
        if not self._dirty:
            return

        data = pygame.image.tobytes(self.surface, "RGBA", False)

        self._set_tex(
            self.ctx.texture(
                size=self.surface.get_size(),
                components=4,
                data=data
            )
        )

        self._dirty = False

    def update(self):
        self.render_to_surface()
        self.update_texture()