import pygame
from OpenGL import GL
from .ui_elements import UIText, UIFloat, UIButton, UILineGraph, UIScrollGrid

GL_GPU_MEMORY_INFO_TOTAL_AVAILABLE_MEMORY_NVX = 0x9048
GL_GPU_MEMORY_INFO_CURRENT_AVAILABLE_VIDMEM_NVX = 0x9049

PLAY_TEXT = ["[EDITOR]", ""]

class EditorUI:
    def __init__(self, ui_renderer, engine):
        self.ui_renderer = ui_renderer
        self.engine = engine

    def initialize(self):
        self.ui_renderer.add_quad(
            UIText(
                0.5,
                0.15,
                "",
                pygame.font.SysFont("consolas", 40),
                self.engine.ctx,
                (255,255,255),
                "centre"
            )
        )

        self.ui_renderer.add_quad(
            UIText(
                0.88,
                0.125,
                "",
                pygame.font.SysFont("consolas", 25),
                self.engine.ctx,
                (255,255,255),
                "right"
            )
        )

        self.ui_renderer.add_quad(
            UIText(
                0.88,
                0.15,
                "",
                pygame.font.SysFont("consolas", 25),
                self.engine.ctx,
                (255,255,255),
                "right"
            )
        )

        self.ui_renderer.add_quad(
            UIText(
                0.88,
                0.175,
                "",
                pygame.font.SysFont("consolas", 25),
                self.engine.ctx,
                (255,255,255),
                "right"
            )
        )

        self.ui_renderer.add_quad(
            UIText(
                0.88,
                0.2,
                "",
                pygame.font.SysFont("consolas", 25),
                self.engine.ctx,
                (255,255,255),
                "right"
            )
        )

        self.ui_renderer.add_quad(
            UIText(
                0.88,
                0.225,
                "",
                pygame.font.SysFont("consolas", 25),
                self.engine.ctx,
                (255,255,255),
                "right"
            )
        )

        self.ui_renderer.add_quad(
            UIText(
                0.88,
                0.25,
                "",
                pygame.font.SysFont("consolas", 25),
                self.engine.ctx,
                (255,255,255),
                "right"
            )
        )

        self.ui_renderer.add_quad(
            UIFloat(
                0.15,
                0.18,
                "Exposure:",
                1.5,
                pygame.font.SysFont("consolas", 25),
                self.engine.ctx,
                (255,255,255),
                "left"
            )
        )

        self.ui_renderer.add_quad(
            UIButton(
                0.15,
                0.205,
                0.1,
                self.engine.ctx,
                "assets/textures/DefaultButton.png",
                "left"
            )
        )

        self.ui_renderer.add_quad(
            UIText(
                0.166,
                0.205,
                "Save Scene",
                pygame.font.SysFont("consolas", 25),
                self.engine.ctx,
                anchor="left"
            )
        )

        self.ui_renderer.add_quad(
            UIButton(
                0.15,
                0.225,
                0.1,
                self.engine.ctx,
                "assets/textures/DefaultButton.png",
                "left"
            )
        )

        self.ui_renderer.add_quad(
            UIText(
                0.166,
                0.225,
                "Load Scene",
                pygame.font.SysFont("consolas", 25),
                self.engine.ctx,
                anchor="left"
            )
        )

        self.ui_renderer.add_quad(
            UILineGraph(
                0.8,
                0.12,
                450,
                300,
                2,
                self.engine.ctx,
                "top_right"
            )
        )

        #self.ui_renderer.add_quad(
        #    UIScrollGrid(
        #        0.5,
        #        0.88,
        #        2000,
        #        400,
        #        self.engine.ctx,
        #        "bottom"
        #    )
        #)

    def update(self, play_mode, fps, dt, dt_real, curr_mem_usage, total_kb, camera_system):
        self.ui_renderer.get_quad(0).update_text(PLAY_TEXT[play_mode])
        self.ui_renderer.get_quad(1).update_text(f"fps: {fps:.1f}")
        self.ui_renderer.get_quad(2).update_text(f"fps_raw: {1/dt_real if dt_real > 0 else float('inf'):.1f}")
        self.ui_renderer.get_quad(3).update_text(f"mem: {curr_mem_usage:.1f}MB")
        
        available_kb = GL.glGetIntegerv(GL_GPU_MEMORY_INFO_CURRENT_AVAILABLE_VIDMEM_NVX)
        used_kb = total_kb - available_kb
        self.ui_renderer.get_quad(4).update_text(f"vram: {used_kb / 1024:.1f}MB")

        self.ui_renderer.get_quad(5).update_text(f"dt: {dt*1000:.1f}ms")
        self.ui_renderer.get_quad(6).update_text(f"dt_raw: {dt_real*1000:.1f}ms")

        exposure_ui = self.ui_renderer.get_quad(7)
        exposure_ui.update()
        for eid in camera_system.em.query("Camera", "Transform"):
            cam = camera_system.em.entities[eid]
            cam.components["Camera"].exposure = exposure_ui.value

        if self.ui_renderer.get_quad(8).update():
            print("\nSCENE SAVED")
            self.engine.save()
        
        if self.ui_renderer.get_quad(10).update():
            print("\nSCENE LOADED")
            return self.engine.initialize()
        
        line_graph = self.ui_renderer.get_quad(12)
        line_graph.add_value(dt*1000, 0, "dt (ms)")
        line_graph.add_value(dt_real*1000, 1, "dt_real (ms)")

        line_graph.update()

        #asset_browser = self.ui_renderer.get_quad(13)
        #asset_browser.update()

        return None