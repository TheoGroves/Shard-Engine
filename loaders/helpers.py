import numpy as np
from numba import njit

@njit
def compute_tangents(vertices, uvs, indices, uv_indices):
    n_verts = vertices.shape[0]

    tangents = np.zeros((n_verts, 3), dtype=np.float32)
    bitangents = np.zeros((n_verts, 3), dtype=np.float32)

    for t in range(indices.shape[0]):

        i0 = indices[t, 0]
        i1 = indices[t, 1]
        i2 = indices[t, 2]

        uv0_i = uv_indices[t, 0]
        uv1_i = uv_indices[t, 1]
        uv2_i = uv_indices[t, 2]

        if uv0_i < 0 or uv1_i < 0 or uv2_i < 0:
            continue

        v0x, v0y, v0z = vertices[i0]
        v1x, v1y, v1z = vertices[i1]
        v2x, v2y, v2z = vertices[i2]

        uv0x, uv0y = uvs[uv0_i]
        uv1x, uv1y = uvs[uv1_i]
        uv2x, uv2y = uvs[uv2_i]

        e1x = v1x - v0x
        e1y = v1y - v0y
        e1z = v1z - v0z

        e2x = v2x - v0x
        e2y = v2y - v0y
        e2z = v2z - v0z

        du1 = uv1x - uv0x
        dv1 = uv1y - uv0y
        du2 = uv2x - uv0x
        dv2 = uv2y - uv0y

        denom = du1 * dv2 - du2 * dv1
        if abs(denom) < 1e-8:
            continue

        f = 1.0 / denom

        tx = f * (dv2 * e1x - dv1 * e2x)
        ty = f * (dv2 * e1y - dv1 * e2y)
        tz = f * (dv2 * e1z - dv1 * e2z)

        bx = f * (-du2 * e1x + du1 * e2x)
        by = f * (-du2 * e1y + du1 * e2y)
        bz = f * (-du2 * e1z + du1 * e2z)

        tangents[i0, 0] += tx
        tangents[i0, 1] += ty
        tangents[i0, 2] += tz

        tangents[i1, 0] += tx
        tangents[i1, 1] += ty
        tangents[i1, 2] += tz

        tangents[i2, 0] += tx
        tangents[i2, 1] += ty
        tangents[i2, 2] += tz

        bitangents[i0, 0] += bx
        bitangents[i0, 1] += by
        bitangents[i0, 2] += bz

        bitangents[i1, 0] += bx
        bitangents[i1, 1] += by
        bitangents[i1, 2] += bz

        bitangents[i2, 0] += bx
        bitangents[i2, 1] += by
        bitangents[i2, 2] += bz

    return tangents, bitangents


def build_interleaved(vertices, normals, tangents, bitangents, uvs,
                      indices, normal_indices, uv_indices):

    vertex_map = {}
    packed = []
    new_indices = []

    for i in range(len(indices)):
        v_i = indices[i]
        n_i = normal_indices[i]
        uv_i = uv_indices[i]

        key = (v_i, n_i, uv_i)

        if key not in vertex_map:
            pos = vertices[v_i]

            # UV
            if uv_i != -1:
                uv = uvs[uv_i]
                u, v = uv[0], uv[1]
            else:
                u, v = 0.0, 0.0

            # Normal
            if n_i != -1:
                norm = normals[n_i]
                nx, ny, nz = norm[0], norm[1], norm[2]
            else:
                nx, ny, nz = 0.0, 0.0, 1.0

            t = tangents[v_i]

            packed.extend([
                pos[0], pos[1], pos[2],
                u, v,
                nx, ny, nz,
                t[0], t[1], t[2]
            ])

            vertex_map[key] = len(vertex_map)

        new_indices.append(vertex_map[key])

    return (
        np.array(packed, dtype="f4"),
        np.array(new_indices, dtype=np.uint32)
    )
