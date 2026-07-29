import sys

sys.path.append("shard/maths/python/Release")

import os
import configparser

config = configparser.ConfigParser()
config.read("build_config.ini")

if config.getboolean("windows", "use_ucrt64_dll_path", fallback=False):
    path = config.get("windows", "ucrt64_path", fallback="")

    if path:
        os.add_dll_directory(path)

from shard_maths import Vec3, Mat4, translate, perspective, look_at, model_matrix, length, normalize, round_to, radians, degrees

__all__ = [
    "Vec3",
    "Mat4",
    "translate",
    "perspective",
    "look_at",
    "model_matrix",
    "length",
    "normalize",
    "round_to", 
    "radians", 
    "degrees"
]