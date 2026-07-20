from ..entity import EntityManager
from rendering import Camera, update_camera_vectors
from core.logger import *

class CameraSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
        self.render_camera = Camera() # c++ handled viewport

    def get_camera(self, eid):
        return self.entity_manager.entities[eid].components["Camera"]

    def update(self, logger):
        cameras = self.entity_manager.query("Transform", "Camera")

        if not cameras:
            logger.log_warning("No cameras found in scene.")

        if not any(self.get_camera(eid).active for eid in cameras):
            logger.log_warning("No active cameras found in scene.")

        if sum(self.get_camera(eid).active for eid in cameras) > 1:
            logger.log_warning("Several active cameras found in scene.")

        for eid in cameras:
            cam = self.get_camera(eid)
            if not cam.active:
                continue

            transform = self.entity_manager.entities[eid].components["Transform"]

            self.render_camera.position = transform.pos
            self.render_camera.rotation = transform.rot

            update_camera_vectors(self.render_camera)