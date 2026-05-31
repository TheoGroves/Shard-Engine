import numpy as np

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
        v = d1 / (d1 - d3)
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

def capsule_triangle_collision(capsule, a, b, c):
    p0, p1 = capsule.get_segment()

    center = (p0 + p1) * 0.5

    closest = closest_point_on_triangle(
        center,
        a,
        b,
        c
    )

    delta = center - closest

    dist = np.linalg.norm(delta)

    if dist >= capsule.radius:
        return None

    if dist < 0.0001:
        normal = np.array([0,1,0], dtype=np.float32)
    else:
        normal = delta / dist

    penetration = capsule.radius - dist

    return normal * penetration