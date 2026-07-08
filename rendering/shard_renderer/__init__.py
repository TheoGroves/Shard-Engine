import os
import configparser

config = configparser.ConfigParser()
config.read("renderer_config.ini")

if config.getboolean("windows", "use_ucrt64_dll_path", fallback=False):
    path = config.get("windows", "ucrt64_path", fallback="")

    if path:
        os.add_dll_directory(path)

from .Release.shard_render_engine import Vec3, Mat4, translate, perspective, look_at, Engine, Camera, forward_from_euler, update_camera_vectors, Input, PlayerController

__all__ = [
    "Vec3",
    "Mat4",
    "translate",
    "perspective",
    "look_at",
    "Engine",
    "Camera",
    "forward_from_euler",
    "update_camera_vectors",
    "Input",
    "PlayerController"
]
