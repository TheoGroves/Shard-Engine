import numpy as np
from collisions.spatial_grid import SpatialGrid

def closest_point_on_triangle(p, a, b, c):
    ab = b - a
    ac = c - a
    ap = p - a

    d1 = np.dot(ab, ap)
    d2 = np.dot(ac, ap)

    if d1 <= 0 and d2 <= 0:
        return a

    bp = p - b
    d3 = np.dot(ab, bp)
    d4 = np.dot(ac, bp)

    if d3 >= 0 and d4 <= d3:
        return b

    vc = d1 * d4 - d3 * d2
    if vc <= 0 and d1 >= 0 and d3 <= 0:
        den = (d1 - d3)
        if abs(den) < 1e-8:
            v = 0.0
        else:
            v = d1 / den

        v = max(0.0, min(1.0, v))
        return a + ab * v

    cp = p - c
    d5 = np.dot(ab, cp)
    d6 = np.dot(ac, cp)

    if d6 >= 0 and d5 <= d6:
        return c

    vb = d5 * d2 - d1 * d6
    if vb <= 0 and d2 >= 0 and d6 <= 0:
        w = d2 / (d2 - d6)
        return a + ac * w

    va = d3 * d6 - d5 * d4
    if va <= 0 and (d4-d3) >= 0 and (d5-d6) >= 0:
        w = (d4-d3) / ((d4-d3)+(d5-d6))
        return b + (c-b) * w

    denom = 1.0 / (va + vb + vc)
    v = vb * denom
    w = vc * denom

    return a + ab*v + ac*w

def sphere_triangle_collision(center, radius, a, b, c):
    closest = closest_point_on_triangle(center, a, b, c)

    delta = center - closest
    dist = np.linalg.norm(delta)

    if dist >= radius:
        return None

    if dist < 1e-6:
        normal = np.array([0, 1, 0], dtype=np.float32)
    else:
        normal = delta / dist

    return normal * (radius - dist)

def get_segment(position, capsule):
    half = max(0.0, capsule.height * 0.5 - capsule.radius)

    p0 = position + np.array([0, -half+capsule.offset, 0], dtype=np.float32)
    p1 = position + np.array([0, half+capsule.offset, 0], dtype=np.float32)

    return p0, p1

def capsule_triangle_collision(position, capsule, a, b, c):
    p0, p1 = get_segment(position, capsule)

    correction = np.zeros(3, dtype=np.float32)

    hit0 = sphere_triangle_collision(
        p0,
        capsule.radius,
        a, b, c
    )

    hit1 = sphere_triangle_collision(
        p1,
        capsule.radius,
        a, b, c
    )

    if hit0 is not None:
        correction += hit0

    if hit1 is not None:
        correction += hit1

    if np.linalg.norm(correction) < 1e-6:
        return None

    return correction

def solve_capsule(transform, capsule, triangles, grid: SpatialGrid):
    grounded = False
    ground_normal = np.zeros(3)
    r = capsule.radius

    mins = transform.pos - np.array([r,1.0,r], dtype=np.float32)
    maxs = transform.pos + np.array([r,1.0,r], dtype=np.float32)

    candidates = grid.query_capsule(
        mins,
        maxs
    )

    for tri_idx in candidates:
        a,b,c = triangles[tri_idx]

        correction = capsule_triangle_collision(
            transform.pos,
            capsule,
            a,b,c
        )

        if correction is not None:
            transform.pos += correction

            n = correction / np.linalg.norm(correction)

            if n[1] > 0.5:
                grounded = True
                ground_normal = n

    return grounded, ground_normal