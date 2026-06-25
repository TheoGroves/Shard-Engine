import time

from core.systems import PlayerControllerSystem
from collisions import SpatialGrid
import spatial_collision_engine as sce

class Engine:
    def __init__(self, ctx, scene, renderer, mesh_collider_system, play_mode):
        self.ctx = ctx
        self.scene = scene
        self.renderer = renderer
        self.mesh_collider_system = mesh_collider_system
        self.play_mode = play_mode

    def initialize(self):
        t = time.perf_counter()
        self.scene.load_scene("main", self.ctx)
        print(f"Scene loaded from disk in {(time.perf_counter()-t)*1000:.1f}ms")

        t = time.perf_counter()
        self.scene.generate_buffers()
        print(f"Buffer generation took {(time.perf_counter()-t)*1000:.1f}ms")

        t = time.perf_counter()
        for eid in self.scene.em.query("Camera"):
            if self.scene.em.entities[eid].components["Camera"].active:
                cam_eid = eid
                break

        cam_t = self.scene.em.entities[cam_eid].components["Transform"]
        cam = self.scene.em.entities[cam_eid].components["Camera"]

        self.renderer.set_camera(cam_t, cam)
        print(f"Camera fetch took {(time.perf_counter()-t)*1000:.1f}ms")

        t = time.perf_counter()
        player_controller_system = PlayerControllerSystem(self.scene.em, cam_t, self.play_mode)

        for eid in self.scene.em.query("PlayerController"):
            player_eid = eid
        
        print(f"Player setup and fetch took {(time.perf_counter()-t)*1000:.1f}ms")

        t = time.perf_counter()
        grid = sce.SpatialGrid(20)
        triangles = self.mesh_collider_system.get_collision_triangles(grid)
        print(f"Collision mesh generation took {(time.perf_counter()-t)*1000:.1f}ms\n")
        
        return cam_t, cam, player_controller_system, player_eid, grid, triangles
    
    def save(self):
        self.scene.save_scene("main")