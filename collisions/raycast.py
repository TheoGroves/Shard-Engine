from numba import njit
import numpy as np

@njit
def ray_triangle_intersection(origin, dir, v0, v1, v2):
    EPS = 1e-8

    origin = origin.astype(np.float32)
    dir = dir.astype(np.float32)
    v0 = v0.astype(np.float32)
    v1 = v1.astype(np.float32)
    v2 = v2.astype(np.float32)

    edge1 = v1 - v0
    edge2 = v2 - v0

    h = np.cross(dir, edge2)
    a = np.dot(edge1, h)

    if abs(a) < EPS:
        return -1.0
    
    f = 1.0 / a
    s = origin - v0
    u = f * np.dot(s, h)

    if u < 0.0 or u > 1.0:
        return -1.0
    
    q = np.cross(s, edge1)
    v = f * np.dot(dir, q)

    if v < 0.0 or u + v > 1.0:
        return -1.0
    
    t = f * np.dot(edge2, q)

    if t > EPS:
        return t
    
    return -1.0

def raycast(ray_o, ray_d, grid, triangles):
    best_t = float("inf")
    hit_point = None
    hit_tri = None

    candidates = grid.query_capsule(
        np.minimum(ray_o, ray_o + ray_d * 1000),
        np.maximum(ray_o, ray_o + ray_d * 1000)
    )

    for tri_index in candidates:
        v0, v1, v2 = triangles[tri_index]

        t = ray_triangle_intersection(ray_o, ray_d, v0, v1, v2)

        if t is not None and t < best_t and t > 0.0:
            best_t = t
            hit_point = ray_o + ray_d * t
            hit_tri = tri_index

    return hit_point, hit_tri