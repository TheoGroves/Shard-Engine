from ..entity import EntityManager
from shard.rendering import Camera, update_camera_vectors
from shard.core.logger import *

class CameraSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
        self.render_camera = Camera() # c++ handled viewport

    def get_camera(self, eid):
        return self.entity_manager.entities[eid].components["Camera"]

    def update(self, logger):
        cameras = self.entity_manager.query("Transform", "Camera")

        if not cameras:
            #logger.log_warning("No cameras found in scene.")
            pass

        elif not any(self.get_camera(eid).active for eid in cameras):
            #logger.log_warning("No active cameras found in scene.")
            pass

        elif sum(self.get_camera(eid).active for eid in cameras) > 1:
            #logger.log_warning("Several active cameras found in scene.")
            pass

        for eid in cameras:
            cam = self.get_camera(eid)
            if not cam.active:
                continue

            transform = self.entity_manager.entities[eid].components["Transform"]

            self.render_camera.position = transform.world_pos
            self.render_camera.forward = transform.world_forward
            self.render_camera.right = transform.world_right
            self.render_camera.up = transform.world_up
            self.render_camera.near_plane = cam.near_plane
            self.render_camera.far_plane = cam.far_plane