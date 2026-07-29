import numpy as np
import spatial_collision_engine as sce

def solve_capsule(transform, capsule, triangles, bvh):
    t_pos = transform.pos
    cap = sce.Capsule(capsule.radius, capsule.height, capsule.offset)

    grounded_data = sce.solve_capsule(t_pos, cap, triangles, bvh)

    transform.pos = t_pos

    return grounded_data.collision, grounded_data.collision_vector