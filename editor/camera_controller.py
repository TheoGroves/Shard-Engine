from maths.python import Vec3, length, normalize

class CameraController:
    def __init__(self):
        self.move_speed = 5
        self.mouse_sensitivity = 0.0025

    def update(self, cam_t, player_input, dt):
        move_dir = Vec3(0,0,0)

        if player_input.sprint:
            self.move_speed = 10
        else:
            self.move_speed = 5

        if player_input.forward:
            move_dir = move_dir + cam_t.forward

        if player_input.backward:
            move_dir = move_dir - cam_t.forward

        if player_input.right:
            move_dir = move_dir + cam_t.right

        if player_input.left:
            move_dir = move_dir - cam_t.right

        if player_input.up:
            move_dir = move_dir + cam_t.world_up

        if player_input.down:
            move_dir = move_dir - cam_t.world_up

        if length(move_dir) > 0.0:
            cam_t.pos = cam_t.pos + normalize(move_dir) * self.move_speed * dt

        cam_t.rot.y += player_input.mouse_dx * self.mouse_sensitivity
        cam_t.rot.x += player_input.mouse_dy * self.mouse_sensitivity

        if cam_t.rot.x > 1.5: cam_t.rot.x = 1.5
        if cam_t.rot.x < -1.5: cam_t.rot.x = -1.5