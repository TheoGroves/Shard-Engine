import numpy as np
import spatial_collision_engine as sce

def solve_capsule(transform, capsule, triangles, bvh):
    grounded = False
    ground_normal = np.zeros(3)

    t_pos = sce.Vec3(transform.pos[0], transform.pos[1], transform.pos[2])
    cap = sce.Capsule(capsule.radius, capsule.height, capsule.offset)

    grounded_data = sce.solve_capsule(t_pos, cap, triangles, bvh)

    transform.pos = np.array([t_pos.x, t_pos.y, t_pos.z])

    grounded = grounded_data.collision
    ground_normal = np.array([grounded_data.collision_vector.x, grounded_data.collision_vector.y, grounded_data.collision_vector.z])

    return grounded, ground_normal