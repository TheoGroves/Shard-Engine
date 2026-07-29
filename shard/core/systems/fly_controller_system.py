from ..entity import EntityManager
from shard.maths.python import Vec3, length, normalize

class FlyControllerSystem:
    def __init__(self, em: EntityManager, render_engine):
        self.em = em
        self.render_engine = render_engine

    def update(self, player_input, dt):
        for eid in self.em.query("FlyController", "Transform"):
            entity = self.em.entities[eid]
            transform = entity.components["Transform"]
            fly_controller = entity.components["FlyController"]

            move_dir = Vec3(0,0,0)

            if player_input.sprint:
                fly_controller.current_speed = fly_controller.boost_speed
            else:
                fly_controller.current_speed = fly_controller.move_speed

            if player_input.forward:
                move_dir = move_dir + transform.world_forward

            if player_input.backward:
                move_dir = move_dir - transform.world_forward

            if player_input.right:
                move_dir = move_dir + transform.world_right

            if player_input.left:
                move_dir = move_dir - transform.world_right

            if player_input.up:
                move_dir = move_dir + Vec3(0,1,0)

            if player_input.down:
                move_dir = move_dir - Vec3(0,1,0)

            # Toggle mouse on escape
            if player_input.escape:
                if not fly_controller.escape_last_frame:
                    fly_controller.mouse_hidden = not fly_controller.mouse_hidden
                fly_controller.escape_last_frame = True
            else:
                fly_controller.escape_last_frame = False

            if fly_controller.mouse_hidden:
                self.render_engine.hide_mouse()
            else:
                self.render_engine.show_mouse()

            if length(move_dir) > 0.0:
                transform.pos = transform.pos + normalize(move_dir) * fly_controller.current_speed * dt

            if fly_controller.mouse_hidden:
                transform.rot.y -= player_input.mouse_dx * fly_controller.mouse_sensitivity
                transform.rot.x -= player_input.mouse_dy * fly_controller.mouse_sensitivity

            if transform.rot.x > 90: transform.rot.x = 90
            if transform.rot.x < -90: transform.rot.x = -90