import numpy as np
import math

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

def get_model_matrix(pos, rot):
    x, y, z = pos
    pitch, yaw, roll = rot

    pitch = math.radians(pitch)
    yaw = math.radians(yaw)
    roll = math.radians(roll)

    rx = np.array([
        [1, 0, 0, 0],
        [0, np.cos(pitch), -np.sin(pitch), 0],
        [0, np.sin(pitch),  np.cos(pitch), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

    ry = np.array([
        [ np.cos(yaw), 0, np.sin(yaw), 0],
        [0, 1, 0, 0],
        [-np.sin(yaw), 0, np.cos(yaw), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

    rz = np.array([
        [np.cos(roll), -np.sin(roll), 0, 0],
        [np.sin(roll),  np.cos(roll), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

    translation = np.eye(4, dtype=np.float32)
    translation[0, 3] = x
    translation[1, 3] = y
    translation[2, 3] = z

    rotation = rz @ ry @ rx

    return translation @ rotation

def get_projection_matrix(camera):
    return perspective(camera.fov, camera.aspect, camera.near, camera.far)

def get_view_matrix(camera):
    return look_at(camera.position, camera.position + camera.front, camera.world_up)

def orthographic(left, right, bottom, top, near, far):
    mat = np.eye(4, dtype=np.float32)

    mat[0,0] = 2 / (right - left)
    mat[1,1] = 2 / (top - bottom)
    mat[2,2] = -2 / (far - near)

    mat[0,3] = -(right + left) / (right - left)
    mat[1,3] = -(top + bottom) / (top - bottom)
    mat[2,3] = -(far + near) / (far - near)

    return mat