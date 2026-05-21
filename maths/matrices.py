import numpy as np

def normalize(v):
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / n

def look_at(eye, target, up):
    eye = np.array(eye, dtype=np.float32)
    target = np.array(target, dtype=np.float32)
    up = np.array(up, dtype=np.float32)

    forward = normalize(target - eye)
    right = normalize(np.cross(forward, up))
    true_up = np.cross(right, forward)

    mat = np.eye(4, dtype=np.float32)

    mat[0, 0:3] = right
    mat[1, 0:3] = true_up
    mat[2, 0:3] = -forward

    mat[0, 3] = -np.dot(right, eye)
    mat[1, 3] = -np.dot(true_up, eye)
    mat[2, 3] = np.dot(forward, eye)

    return mat

def perspective(fov, aspect, near, far):
    f = 1.0 / np.tan(np.radians(fov) / 2.0)

    mat = np.zeros((4, 4), dtype=np.float32)

    mat[0, 0] = f / aspect
    mat[1, 1] = f

    mat[2, 2] = (far + near) / (near - far)
    mat[2, 3] = (2 * far * near) / (near - far)

    mat[3, 2] = -1.0

    return mat

def get_model_matrix(pos):
    x, y, z = pos
    mat = np.eye(4, dtype=np.float32)
    mat[0, 3] = x * 16
    mat[1, 3] = y * 16
    mat[2, 3] = z * 16
    return mat

def get_projection_matrix(camera):
    return perspective(camera.fov, camera.aspect, camera.near, camera.far)

def get_view_matrix(camera):
    return look_at(camera.position, camera.position + camera.front, camera.world_up)