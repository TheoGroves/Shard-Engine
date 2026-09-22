import time
import spatial_collision_engine as sce
from shard_maths import Vec3
from shard.core.logger import *

def raycast(ray_o, ray_d, bvh, triangles, logger):
    #s = time.perf_counter()

    ray_hit = sce.raycast(ray_o, ray_d, triangles, bvh)

    #logger.log_info(f"Raycast took {(time.perf_counter()-s)*1000:.1f}ms")

    return ray_hit.point, ray_hit.tri_index, ray_hit.distance