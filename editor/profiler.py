import heapq
from rendering import RenderEngine

class Profiler:
    def __init__(self, render_engine: RenderEngine):
        self.render_engine = render_engine
        self.dt_history = []

    def update(self, dt):
        self.dt_history.append(dt)
        if len(self.dt_history) > 200:
            self.dt_history.pop(0)

        total_frames = len(self.dt_history)
        if total_frames == 0:
            return
        
        avg_dt = sum(self.dt_history) / total_frames
        avg_fps = 1.0 / avg_dt

        count = max(1, int(total_frames * 0.01))
        worst_frames = heapq.nlargest(count, self.dt_history)

        avg_worst_dt = sum(worst_frames) / count
        low_fps = 1.0 / avg_worst_dt

        self.render_engine.begin_window("Profiler")

        self.render_engine.text(f"FPS: {avg_fps:.1f} ({avg_dt*1000:.1f}ms)")
        self.render_engine.text(f"1% Low FPS: {low_fps:.1f} ({avg_worst_dt*1000:.1f}ms)")
        self.render_engine.end_window()