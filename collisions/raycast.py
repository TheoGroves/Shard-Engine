import numpy as np
import time
import spatial_collision_engine as sce
from shard_maths import Vec3
from core.logger import *

def raycast(ray_o, ray_d, bvh, triangles, logger):
    s = time.perf_counter()
    origin = Vec3(ray_o[0], ray_o[1], ray_o[2])
    dir = Vec3(ray_d[0], ray_d[1], ray_d[2])

    ray_hit = sce.raycast(origin, dir, triangles, bvh)

    logger.log_info(f"Raycast took {(time.perf_counter()-s)*1000:.1f}ms")

    return np.asarray([ray_hit.point.x, ray_hit.point.y, ray_hit.point.z]), ray_hit.tri_index